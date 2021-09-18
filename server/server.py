import socket

HOST = '0.0.0.0'
PORT = 6669

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
global pi
pi=None


from flask import Flask, render_template
from flask_socketio import SocketIO
app = Flask(__name__)
socketio = SocketIO(app)
if __name__ == '__main__':
    socketio.run(app, port=8002)
    
@socketio.event
def connection(sid):
    print(f'Connection from {sid}')

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

# while True:
#     # Establish connection with client.
#     c, addr = s.accept()
#     print('Got connection from', addr)

#     # send a thank you message to the client. encoding to send byte type.
#     c.send('connect_confirmation'.encode())
#     pi=c
#     while (True):
#         print(c.recv(1024).decode())

# c.close()
