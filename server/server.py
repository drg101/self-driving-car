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

pi = None
socketApp = Flask(__name__)
videoApp = Flask("videoApp")

sio = SocketIO(socketApp, cors_allowed_origins="*")
outputFrame = None
lock = threading.Lock()

CONTROL_PORT = 6669
SOCKET_PORT = 8002
VIDEO_PORT = 8003
HOST = '0.0.0.0'



def controlPI(controlJSON):
    global pi
    if pi != None:
        pi.send(str(controlJSON).encode())

def controlServer():
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


def videoServer():
    global outputFrame,lock,videoApp
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
                with lock: 
                    outputFrame = img.copy()
                # cv2.imshow('frame', img)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
            dat = b''

    # cap.release()
    # cv2.destroyAllWindows()
    # s.close()


def videoStreamerServer():
    videoApp.run(host=HOST, port=VIDEO_PORT, debug=False, use_reloader=False) # dont touch this shit!

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if outputFrame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')
  
@videoApp.route("/video_feed")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    controlThread = threading.Thread(target=controlServer, args=[]).start()
    videoThread = threading.Thread(target=videoServer, args=[]).start()
    videoStreamerThread = threading.Thread(target=videoStreamerServer, args=[]).start()
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
    sio.run(socketApp, host=HOST, port=SOCKET_PORT)
