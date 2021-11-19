from control import forward, backward, left, right, setTurnStrength, straight, stop, setSpeed
import socket            
import json
import threading
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import socket
import struct
import math
from PiVideoStream import PiVideoStream

serverip = '192.168.0.112'
videoRes = (640, 480)
videoFps = 30
imReady = False
currIm = None
newFrame = False

# Thread that creates a thread that connects to the server @serverip
def controlScript():
    s = socket.socket()        
    
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
                    if fw > 0:
                        setSpeed(math.floor(fw * 100))
                        forward()
                    elif fw < 0:
                        setSpeed(math.floor(abs(fw) * 100))
                        backward()
                    else:
                        stop()
                
                if oldLr != lr:
                    oldLr = lr
                    if lr > 0:
                        right()
                    elif lr < 0:
                        left()
                    else:
                        straight()
                    setTurnStrength(math.floor(abs(lr) * 100))

# From a blog post
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
        # rs_img = cv2.resize(img, (videoRes[0] // 2, videoRes[1] // 2)) 
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        # print(size)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        #print(count)
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1

def videoUploader():
    # make da socket on port port 6670
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = 6670

    # this is the thing that sends it to the server
    fs = FrameSegment(s, port)
    prevTime = 0
    vs = PiVideoStream()
    vs.start()
    time.sleep(2.0)
    while True:
        if time.time() - prevTime >= 1 / 30:
            # print(1 / (time.time() - prevTime))
            prevTime = time.time()
            fs.udp_frame(vs.read())

if __name__ == "__main__":
    controlThread = threading.Thread(target=controlScript, args=[])
    controlThread.start()
    videoUploadThread = threading.Thread(target=videoUploader, args=[])
    videoUploadThread.start()
