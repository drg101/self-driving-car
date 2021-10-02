from __future__ import division
from control import forward, backward, left, right, straight, stop, setSpeed
import socket            
import json
import threading
import time
 

def controlScript():
    # Create a socket object
    s = socket.socket()        
    
    # Define the port on which you want to connect
    port = 6669             
    
    # connect to the server on local computer
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect(('192.168.241.58', port))

    straight()
    stop() 
    oldFw = 0
    oldLr = 0

    while(True):
        controlStringsString = s.recv(1024).decode()
        controlStringsArray = controlStringsString.split('@')
        for controlString in controlStringsArray:
            if '{' in controlString or '}' in controlString:
                #controlString = controlString.replace("'", '"')
                controlJSON = json.loads(controlString)
                #print('JSON: ', controlJSON)
                fw = controlJSON['fw']
                lr = controlJSON['lr']
                if oldFw != fw:
                    oldFw = fw
                    if fw == 1:
                        forward()
                    elif fw == -1:
                        backward()
                    else:
                        stop()
                
                if oldLr != lr:
                    oldLr = lr
                    if lr == 1:
                        right()
                    elif lr == -1:
                        left()
                    else:
                        straight()

import cv2
import numpy as np
import socket
import struct
import math


class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="192.168.241.58"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1

def videoScript():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 6670

    fs = FrameSegment(s, port)

    cap = cv2.VideoCapture(0)
    frame_rate = 5
    prev = 0
    while (cap.isOpened()):
        time_elapsed = time.time() - prev
        if time_elapsed > 1./frame_rate:
            prev = time.time()
            _, frame = cap.read()
            fs.udp_frame(frame)

    cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    controlThread = threading.Thread(target=controlScript, args=[])
    controlThread.start()
    videoThread = threading.Thread(target=videoScript, args=[])
    videoThread.start()
