import serial
import zmq
from time import time,sleep
import socket
import sys

def checkPupilPlayer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',50020))
    
    if result == 0:
        print 'Found Pupil Capture'
   
    else:
        print 'Cannot find Pupil Capture'
        sys.exit()
    
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
        print 'Cannot connect to Pupil Capture'
        sys.exit()
    
    print 'Connected to Pupil Capture'
    print 'Current timestamp from Pupil Capture:', tStamp
    print 'Round trip command delay:', t2-t1
    
    sleep(1)
    
    return socket    


def connectVicon():
    try:
        ard = serial.Serial('COM10', 115200)#, timeout=.1)
        print 'Found serial port, ready to start Vicon acquisition'       
        
        return ard
    
    except Exception:
        print 'Cannot find Vicon server -- check trigger box is connected to laptop (usb) and Vicon server (av)'
        sys.exit()

    
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
            
    def connectionFailed(self):
        self.connected = False
        print 'Stopped receiving data from Vicon server'
        sys.exit()
   
    
def main():
    
    checkPupilPlayer()

    pupil = connectPupil()
       
    vicon = connectVicon()
    
    try:
        rec = recorder(pupil)
        
        while True:
            data = vicon.read()
            
            if not data:
                rec.connectionFailed()
            
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
        sys.exit()
           
if __name__ == '__main__':
    main()     
