from __future__ import division
import cv2
import numpy as np
import struct
import socket
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
import base64
import time

pi = None
flaskApp = Flask(__name__)
sio = SocketIO(flaskApp, cors_allowed_origins="*")
toEmit = (None, None)


def controlPI(controlJSON):
    global pi
    if pi != None:
        pi.send(str(controlJSON).encode())

def controlServer():
    global pi
    HOST = '0.0.0.0'
    PORT = 6669

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


def videoServer():
    global toEmit
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
            # smol_img = cv2.resize(img, (320, 240))
            if (type(img) is np.ndarray):  
                retval, buffer = cv2.imencode('.jpg', img)
                imgAsBase64 = base64.b64encode(buffer)
                toEmit = ('imgFrame', str(imgAsBase64))
                #emitSocket('imgFrame', imgAsBase64)
                cv2.imshow('frame', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()


def emmisionThread():
    global toEmit
    while(True):
        e = toEmit
        sio.emit(e[0], e[1])
        sio.sleep(1./30)


if __name__ == '__main__':
    controlThread = threading.Thread(target=controlServer, args=[]).start()
    videoThread = threading.Thread(target=videoServer, args=[]).start()
    sio.start_background_task(target=emmisionThread)
    @sio.event
    def connect():
        print(f'Connection from')
        return True

    @sio.event
    def disconnect():
        print(f'disConnection from')
        return True

    @sio.on('my_event')
    def handle_my_custom_event(json):
        print('received control string: ' + json)
        controlPI(json + '@')
    print("here")
    sio.run(flaskApp, host='0.0.0.0', port=8002)
