import serial
import zmq
from time import time,sleep
import socket
import sys

def checkPupilPlayer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',50020))
    
    if result == 0:
       return True
    
    else:
       return False
    
    sock.close()


def connectPupil():
    context =  zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://127.0.0.1:50020')#tcp://192.168.1.100:50020')

    #get timing information
    t1 = time()
    socket.send('t') #'t' get pupil capture timestamp returns a float as string
    tStamp = socket.recv()
    t2 = time()
    
    if not tStamp:
        return False
    
    print 'Connected to Pupil player'
    print 'Current timestamp from Pupil player:', tStamp
    print 'Round trip command delay:', t2-t1
    
    sleep(1)
    
    return socket    


def checkVicon():
    try:
        ard = serial.Serial('COM10', 115200)#, timeout=.1)
        print 'Found serial port, ready to start Vicon acquisition'       
        
        return ard
    
    except Exception:
        return False
    
    
class recorder:
    def __init__(self,socket):
        self.recording = False
        self.connected = False
        self.socket = socket
        
    def record(self):
        self.socket.send('R')
        print 'Recording started:', self.socket.recv()
        self.recording = True
    
    def stop(self):
        self.socket.send('r')
        print 'Recording stopped:', self.socket.recv()
        self.recording = False
            
    def connectMessage(self, message):
        if message == 'c':
            self.connected = True
            print 'Receiving data from Vicon server'
        
        if message == 'f':
            self.connected = False
            print 'Stopped receiving data from Vicon server'
   
    
def main():
    port = checkPupilPlayer()
    
    if not port:
        print 'Cannot find Pupil capture'
        sys.exit()
    
    print 'Found Pupil player'
    
    pupil = connectPupil()
    
    if not pupil:
        print 'Cannot connect to Pupil capture'
        sys.exit()
        
    vicon = checkVicon()
    
    if not vicon:
        print 'Cannot find Vicon server -- check trigger box is connected to laptop (usb) and Vicon server (av)'
        sys.exit()
    
    try:
        rec = recorder(pupil)
        
        while True:
            data = vicon.read()
            
            if not data:
                rec.connectMessage('f')
            
            else:
                if data == 'h':
                    if not rec.recording:
                        rec.record()
                        
                elif data == 'l':
                    if rec.recording:
                        rec.stop()
                                
    except KeyboardInterrupt:
        vicon.close()
        print 'Vicon connection disabled'
           
if __name__ == '__main__':
    main()     