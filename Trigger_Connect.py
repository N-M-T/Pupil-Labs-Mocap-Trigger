import serial
import zmq
from time import time,sleep
import socket
import sys
import os
import datetime

#check pupil capture instance exists
def checkPupilCapture():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',50020))
    
    if result == 0:
        print 'Found Pupil Capture'
   
    else:
        print 'Cannot find Pupil Capture'
        sys.exit()
    
    sock.close()


#connect to pupil capture using zmq protocol
def connectPupil():
    context =  zmq.Context()
    remote = context.socket(zmq.REQ)
    remote.connect('tcp://127.0.0.1:50020')
    
    #get timing information
    t1 = time()
    remote.send('t')
    tStamp = remote.recv()
    t2 = time()
    
    if not tStamp:
        print 'Cannot connect to Pupil Capture'
        sys.exit()
    
    print 'Connected to Pupil Capture'
    print 'Round trip command delay:', t2-t1

    return remote 


#connect to motion capture server via arduino 
def connectMocap():
    try:
        ard = serial.Serial('COM10', 115200)#, timeout=.1)
        print 'Found serial port'       
        
        return ard
    
    except Exception:
        print 'Cannot find Mocap server -- check trigger box is connected to laptop (usb) and Mocap server (av)'
        sys.exit()


#set Pupil Capture's time base to this scripts time (before starting a recording)
def timeSet(remote):
    remote.send_string("T {}".format(time()))
    print(remote.recv_string())
    
    print "Fire (Begin pupil recording and start/stop Mocap acquisition/s) at will, said Jean-Luc Picard"


#save timeStamp to current recording folder
def appendTimestamp(start_stop,value):
    #find todays recording folder
    path = 'C:/Users/Neil Thomas/Desktop/recordings/'
    now = datetime.datetime.now()
    
    year = str(now.year)
    month = str(now.month)
    day = now.day
    
    if day >= 10:
        day = str(day)
    else:
        day = '0'+str(day)
    
    date = year+'_'+'0'+month+'_'+day
    target = [name for name in os.listdir(path) if name == date]
    
    recordings = os.listdir(path+target[0])
    current = max(recordings)
    
    #current path 
    currentPath = path+target[0]+'/'+current+'/'
        
    try:
        file = open(currentPath+'Mocap_timestamps.txt', 'a+')
        file.write(start_stop+value+'\n')
        file.close()
    except:
        file = open(currentPath+'Mocap_timestamps.txt', 'w+')
        file.write(start_stop+value+'\n')
        file.close()

#save timestamp when a mocap acquisition is started/stopped
class trigger:
    def __init__(self, pupil):
        self.recording = False
        self.pupil = pupil
        
    def startTrigger(self):        
        self.pupil.send('t')
        Time = self.pupil.recv()
        self.recording = True

        print 'Mocap recording started:', Time
        
        #save timestamp to current recording folder
        appendTimestamp('start,', Time)
    
    def stopTrigger(self):
        self.pupil.send('t')
        Time = self.pupil.recv()
        self.recording = False
        print 'Mocap recording stopped:', Time
        
        appendTimestamp('end,', Time)
            
    def connectionFailed(self):
        print 'Stopped receiving data from Mocap server'
        sys.exit()
        
   
def main():
    
    checkPupilCapture()

    pupil = connectPupil()
       
    Mocap = connectMocap()
    
    timeSet(pupil)
    
    try:
        rec = trigger(pupil)
        
        while True:
            data = Mocap.read()
            
            if not data:
                rec.connectionFailed()
            
            else:
                if data == 'h':
                    if not rec.recording:
                        rec.startTrigger()
                        
                elif data == 'l':
                    if rec.recording:
                        rec.stopTrigger()          
             
            
    except KeyboardInterrupt:
        Mocap.close()
        print 'Mocap connection disabled'
        sys.exit()
           
        
if __name__ == '__main__':
    main()     
