from __future__ import division
from control import forward, backward, left, right, straight, stop, setSpeed
import socket            
import json
import threading
import time
from picamera.array import PiRGBArray
from picamera import PiCamera

serverip = '192.168.80.58'
videoRes = (640, 480)
videoFps = 60

def controlScript():
    # Create a socket object
    s = socket.socket()        
    
    # Define the port on which you want to connect
    port = 6669             
    
    # connect to the server on local computer
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((serverip, port))

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
    def __init__(self, sock, port, addr=serverip):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        # resized_image = cv2.resize(compress_img, (, 75)) 
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
    camera = PiCamera()
    camera.resolution = videoRes
    camera.framerate = videoFps
    rawCapture = PiRGBArray(camera, size=videoRes)
    # wait for camera to exist
    time.sleep(0.1)
    print("sending video data")

    # make da socket on port port 6670
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 6670

    # this is the thing that sends it to the server
    fs = FrameSegment(s, port)
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array
        fs.udp_frame(image)
        rawCapture.truncate(0)

if __name__ == "__main__":
    controlThread = threading.Thread(target=controlScript, args=[])
    controlThread.start()
    videoThread = threading.Thread(target=videoScript, args=[])
    videoThread.start()
