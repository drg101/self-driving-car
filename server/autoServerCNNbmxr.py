import cv2
import numpy as np
import struct
import socket
import threading
import logging
from pynput import keyboard
import json
from VideoSaver import VideoSaver
from time import time
import os
from pathlib import Path
import time
import pickle


from tensorflow import keras

model = keras.models.load_model('../models/daniel_cnn_bmxr_v1.h5')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

pi = None

newFrame = False

outputFrame = None

piInput = {'lr': 0, 'fw': 0}


CONTROL_PORT = 6669
HOST = '0.0.0.0'

# leftMean = np.load('leftMean.npy')
# rightMean = np.load('rightMean.npy')
# straightMean = np.load('straightMean.npy')
# knn = pickle.load(open('knn_serialized.pickle', 'rb'))

# helper method to control the PI. Pretty self explanatory.
def controlPI(controlJSON):
    global pi
    if pi != None:
        pi.send(str(controlJSON).encode())

# Thread that creates server that the pi TCP connects with on port 6669.
def controlSenderServer():
    global pi
    PORT = CONTROL_PORT

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        # Establish connection with client.
        c, addr = s.accept()
        print('Got connection from', addr)

        # send a thank you message to the client. encoding to send byte type.
        c.send('THANKJ YIOU FOR CONNECTUNG'.encode())
        pi = c
        break

def bmxr(im, x=1.5):
    b = im[:,:,0]
    r = im[:,:,2]
    return cv2.subtract(b,cv2.multiply(r,x))

def thresholdIm(im, low=50, high=255):
    e,im = cv2.threshold(im, low, high, cv2.THRESH_BINARY)
    return im
    
def processIm(im):
    im = cv2.resize(im,(80,60))
    im = bmxr(im,1.25)
    im = thresholdIm(im,8,255)
    return im

def distance(x1, x2):
    return np.linalg.norm(x1-x2)

def predict_direction(img):
    return model(img.reshape(-1,60,80,1))

# Thread that creates a server that the pi UDP connects with on port 6670. This is the one that
# collects video stream data.
def videoReceiverServer():
    MAX_DGRAM = 2**16
    global outputFrame, newFrame, piInput
    def dump_buffer(s):
        """ Emptying buffer frame """
        while True:
            seg, addr = s.recvfrom(MAX_DGRAM)
            print(seg[0])
            if struct.unpack("B", seg[0:1])[0] == 1:
                print("finish emptying buffer")
                break
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 6670))
    dat = b''
    dump_buffer(s)
    oldCtlTime = time.time()
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            # our image
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            if (type(img) is np.ndarray):
                if img.shape[0] > 0 and img.shape[1] > 1:
                    # print(1 / (time.time() - oldTime))
                    img = np.flip(img, (0,1))
                    # outputFrame = img
                    if time.time() - oldCtlTime > 0.1:
                        oldCtlTime = time.time() 
                        driverIm = processIm(img)
                        sP = time.time()
                        direction = predict_direction(driverIm)
                        outputFrame = driverIm
                        print(f'ttp: {time.time() - sP}')
                        direction = direction[0].numpy().argmax() - 1
                        direction = int(direction)
                        print(f'dir: {direction}')
                        piInput['lr'] = direction
                        controlChanged()
                    newFrame = True
            dat = b''
            
def videoShow(saver):
    oldTime = 0 
    global newFrame
    while True:
        if (type(outputFrame) is np.ndarray) and newFrame:
            # print(1 / (time.time() - oldTime))
            oldTime = time.time()
            cv2.imshow("frame",cv2.resize(outputFrame, (1280, 960)))
            newFrame = False
            #saver.save(outputFrame, time.time(), piInput)
            cv2.waitKey(5)

def controlChanged():
    print(f'control: {piInput}')
    controlPI(json.dumps(piInput) + '@')

def onKeyRelease(key):
    try:
        key = key.char
        originalInput = json.dumps(piInput)
        if key == 'w' and piInput['fw'] != -1:
            piInput['fw'] = 0
        elif key == 's' and piInput['fw'] != 1:
            piInput['fw'] = 0
        elif key == 'd' and piInput['lr'] != -1:
            piInput['lr'] = 0
        elif key == 'a' and piInput['lr'] != 1:
            piInput['lr'] = 0
        if json.dumps(piInput) != originalInput:
            controlChanged()
    except:
        pass

def onKeyPress(key):
    try:
        key = key.char
        originalInput = json.dumps(piInput)
        if key == 'w':
            piInput['fw'] = 1
        elif key == 's':
            piInput['fw'] = -1
        elif key == 'd':
            piInput['lr'] = 1
        elif key == 'a':
            piInput['lr'] = -1
        if json.dumps(piInput) != originalInput:
            controlChanged()
    except:
        pass
    
def controlPad(): 
    with keyboard.Listener(on_press = onKeyPress,on_release = onKeyRelease) as listener:
        listener.join()


if __name__ == '__main__':
    saver ='b'
    controlSenderThread = threading.Thread(target=controlSenderServer, args=[]).start()
    videoReceiveThread = threading.Thread(target=videoReceiverServer, args=[]).start()
    controlPad = threading.Thread(target=controlPad, args=[]).start()
    videoShowerThread = threading.Thread(target=videoShow, args=[saver]).start()
    print('server running.')
