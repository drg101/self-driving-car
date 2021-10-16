from __future__ import division
import cv2
import flask
import numpy as np
import struct
import socket
import threading
from flask import Flask, Response
from flask_socketio import SocketIO, send, emit
import base64
import time
from flask_compress import Compress
import logging
from pynput import keyboard
import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
compress = Compress()

pi = None
socketApp = Flask(__name__)

sio = SocketIO(socketApp, cors_allowed_origins="*")
outputFrame = None
q = [int(cv2.IMWRITE_JPEG_QUALITY), 20]

piInput = {'lr': 0, 'fw': 0}


CONTROL_PORT = 6669
SOCKET_PORT = 8002
VIDEO_PORT = 8003
HOST = '0.0.0.0'


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

# Thread that creates a server that the pi UDP connects with on port 6670. This is the one that
# collects video stream data.
def videoReceiverServer():
    MAX_DGRAM = 2**16

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

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            # our image
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            if (type(img) is np.ndarray):
                cv2.imshow("frames",cv2.resize(img, (1280, 960)))
                if cv2.waitKey(1):
                    pass
            dat = b''

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
    controlSenderThread = threading.Thread(target=controlSenderServer, args=[]).start()
    videoReceiveThread = threading.Thread(target=videoReceiverServer, args=[]).start()
    controlPad = threading.Thread(target=controlPad, args=[]).start()
    print('server running.')
