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
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
compress = Compress()

pi = None
socketApp = Flask(__name__)
videoApp = Flask("videoApp")
compress.init_app(videoApp)

sio = SocketIO(socketApp, cors_allowed_origins="*")
outputFrame = None
lock = threading.Lock()
q = [int(cv2.IMWRITE_JPEG_QUALITY), 20]


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
            if (type(img) is np.ndarray):
                cv2.imshow("frames",cv2.resize(img, (1280, 960)))
                if cv2.waitKey(1):
                    pass
                with lock: 
                    outputFrame = cv2.resize(img, (320, 240)).copy()
            dat = b''

# Thread that creates a flask app on port 8003 that transmits the video data to the open world on 0.0.0.0:8003/video_feed
def videoSenderServer():
    videoApp.run(host=HOST, port=VIDEO_PORT, debug=False, use_reloader=False) # dont touch this shit!

# helper, this code was taken from a blog post and thats why it has so many comments
def generateFrame():
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
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame, q)
			# ensure the frame was successfully encoded
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')
  
@videoApp.route("/video_feed")
def video_feed():
	return Response(generateFrame(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


if __name__ == '__main__':
    controlSenderThread = threading.Thread(target=controlSenderServer, args=[]).start()
    videoReceiveThread = threading.Thread(target=videoReceiverServer, args=[]).start()
    videoSenderThread = threading.Thread(target=videoSenderServer, args=[]).start()
    
    # the sio listeners dont play well with threads so they live here now.
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
    sio.run(socketApp, host=HOST, port=SOCKET_PORT, debug=False)
