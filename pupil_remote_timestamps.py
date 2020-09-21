import serial
import serial.tools.list_ports
import zmq
from time import time
import socket
import sys
import os
import datetime


ip = '127.0.0.1'
port = 50020
path = 'C:/Users/Neil Thomas/Desktop/recordings/'


def check_pupil_capture():
    """check pupil capture instance exists"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if not sock.connect_ex((ip, port)):
        print('Found Pupil Capture')
    else:
        print ('Cannot find Pupil Capture')
        sys.exit()
        
    sock.close()


def connect_pupil_capture():
    """connect to pupil capture using zmq protocol"""
    context =  zmq.Context()
    socket = zmq.Socket(context, zmq.REQ)
    socket.connect('tcp://' + ip + ':' + str(port))
    socket.send_string('t')
   
    if not socket.recv():
        print('Cannot connect to Pupil Capture')
        sys.exit()

    return socket 
           

def connect_mocap():
    """
    listen to motion capture server via arduino. Oneway trip time between
    computer and arduino is ~0.5ms
    """
    
    # find arduino
    ports = [p.device for p in serial.tools.list_ports.comports() 
             if 'USB Serial Device' in p.description]
    
    if not ports:
        print('Cannot find arduino. Check connection to computer')
        sys.exit()
    
    if len(ports) > 1:
        print('Multiple arduinos found. Remove redundant ones')
        sys.exit()
    
    
    ard = serial.Serial(ports[0], 115200)
    print('Found arduino')
    
    return ard    


def get_pupil_time(socket):
    t1 = time()
    socket.send_string('t')
    pct = socket.recv()
    t2 = time()
    oneway_dur = (t2-t1) / 2
    return (float(pct.decode()) - oneway_dur) - 0.0005


def append_timestamp(start_stop, value):  
    now = datetime.datetime.now()  
    year = str(now.year)
    month = str(now.month)
    day = now.day
    
    if day >= 10:
        day = str(day)
    else:
        day = '0' + str(day)
    
    date = year + '_' + '0' + month + '_' + day
    target = [name for name in os.listdir(path) if name == date]    
    recordings = os.listdir(path + target[0])
    current = max(recordings)
    currentPath = path + target[0] + '/' + current + '/'
        
    try:
        file = open(currentPath + 'Mocap_timestamps.txt', 'a+')
        file.write(start_stop + ': ' + value + '\n')
        file.close()
    except:
        file = open(currentPath + 'Mocap_timestamps.txt', 'w+')
        file.write(start_stop + ': ' + value + '\n')
        file.close()


class Trigger:
    def __init__(self, socket):
        self.recording = False
        self.socket = socket
        print('Ready to start/stop mocap acquisition...')
        
        
    def start_trigger(self):
        if not self.recording:
            pct = get_pupil_time(self.socket)
            append_timestamp('start', str(pct))
            print('Started mocap acquisition')
            self.recording = True
            
    
    def stop_trigger(self):
        if self.recording:
            pct = get_pupil_time(self.socket)
            append_timestamp('stop', str(pct))
            print('Stopped mocap acquisition')
            self.recording = False
        
        
def main():
    check_pupil_capture()
    socket = connect_pupil_capture()
    ard = connect_mocap()
    trigger = Trigger(socket)
    
    try:
        while True:
            data = ard.read(1)
            
            if data.decode() == 'h':
                trigger.start_trigger()
                
            if data.decode() == 'l':
                trigger.stop_trigger()
    
    except (KeyboardInterrupt, SystemExit):
        print('User exited program')        
        socket.close()
        sys.exit()
    except Exception as err:
        print(err)
        socket.close()
           
        
if __name__ == '__main__':
    main()     
