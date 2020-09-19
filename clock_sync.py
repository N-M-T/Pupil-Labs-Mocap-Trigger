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


def sync_clocks(socket): 
    socket.send_string("T {}".format((time())))
    if socket.recv():
        pass
    
    test_sync(socket)
    
    comp, pct, diff = test_sync(socket)
    
    if diff < 0.01:
        print('comp: ', comp, 'pct :', pct)
        print('Sync accurate to: ~', format(diff, ".3f"), 'ms')
        return diff
    else:
        return sync_clocks(socket)
        

def test_sync(socket):
    t1 = time()
    socket.send_string('t')
    pct = socket.recv()
    t2 = time()
    oneway_dur = (t2-t1) / 2
    corrected_pct = float(pct.decode()) - oneway_dur
    
    return t1, corrected_pct, abs(corrected_pct - t1) * 1000  # scale to ms
    
    
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
        file.write(start_stop + value + '\n')
        file.close()
        
        
class Trigger:
    def __init__(self, socket):
        self.recording = False
        self.socket = socket
        print('Ready to start/stop mocap acquisition...')
        
        
    def start_trigger(self, t):
        if not self.recording:
            append_timestamp('start', str(t))
            print('Started mocap acquisition')
            self.recording = True
            
    
    def stop_trigger(self, t):
        if self.recording:
            append_timestamp('stop', str(t))
            print('Stopped mocap acquisition')
            self.recording = False
        
        
def main():
    check_pupil_capture()
    socket = connect_pupil_capture()
    sync_clocks(socket)
    ard = connect_mocap()
    trigger = Trigger(socket)
    
    try:
        while True:
            data = ard.read(1)
            t = time()
            
            if data.decode() == 'h':
                trigger.start_trigger(t - 0.001)
                
            if data.decode() == 'l':
                trigger.stop_trigger(t - 0.001)
    
    except (KeyboardInterrupt, SystemExit):
        print('User exited program')        
        socket.close()
        sys.exit()
    except Exception as err:
        print(err)
        socket.close()
           
        
if __name__ == '__main__':
    main()     
