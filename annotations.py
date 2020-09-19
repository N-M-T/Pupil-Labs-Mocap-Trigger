import serial.tools.list_ports
import zmq
import socket
import sys
import msgpack as serializer
import time as time


ip = '127.0.0.1'
port = 50020


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
    try:
        context =  zmq.Context()
        socket = zmq.Socket(context, zmq.REQ)
        socket.connect('tcp://' + ip + ':' + str(port))
        socket.send_string("PUB_PORT")
        pub_port = socket.recv_string()
        pub_socket = zmq.Socket(context, zmq.PUB)
        pub_socket.connect('tcp://' + ip + ':{}'.format(pub_port))
        
        return socket, pub_socket
    
    except Exception as err:
       print('Cannot connect to Pupil Capture', err)
       sys.exit()
                         
        
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
    oneway_dur = (t2 - t1) / 2
    
    return  (float(pct.decode()) - oneway_dur) - 0.0005


def new_trigger(label, duration, time_stamp):
    return {"topic": "annotation",
            "label": label,
            "timestamp": time_stamp,
            "duration": duration}


def notify(socket):
    """Sends notification to Pupil Remote"""
    notification = {"subject": "start_plugin", 
                    "name": "Annotation_Capture", 
                    "args": {}}
    
    topic = "notify." + notification["subject"]
    payload = serializer.dumps(notification, use_bin_type=True)
    socket.send_string(topic, flags=zmq.SNDMORE)
    socket.send(payload)
    
    return socket.recv_string()
        

class Trigger:
    def __init__(self, socket, pub_socket):
        self.recording = False
        self.socket = socket
        self.pub_socket = pub_socket
        print('Ready to start/stop mocap acquisition...')
        
    
    def start_trigger(self):
        if not self.recording:
            pct = get_pupil_time(self.socket)
            trigger = new_trigger(label='start',
                                  duration=0,
                                  time_stamp=pct)
            self.send_trigger(trigger)
            
            print('Started mocap acquisition')
            self.recording = True
            
    
    def stop_trigger(self):
        if self.recording:
            pct = get_pupil_time(self.socket)
            trigger = new_trigger(label='stop',
                                  duration=0,
                                  time_stamp=pct)
            self.send_trigger(trigger)
            print('Stopped mocap acquisition')
            self.recording = False
    
    def send_trigger(self, trigger):
        payload = serializer.dumps(trigger, use_bin_type=True)
        self.pub_socket.send_string(trigger["topic"], flags=zmq.SNDMORE)
        self.pub_socket.send(payload)
        
        
def main():
    check_pupil_capture()
    socket, pub_socket = connect_pupil_capture()
    ard = connect_mocap()
    trigger = Trigger(socket, pub_socket)
    notify(socket)
    
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
        pub_socket.close()
        sys.exit()
    except Exception as err:
        print(err)
        socket.close()
        pub_socket.close()
           
        
if __name__ == '__main__':
    main()     
