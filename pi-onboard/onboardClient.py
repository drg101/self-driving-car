from control import forward, backward, left, right, straight, stop, setSpeed
import socket            
 
# Create a socket object
s = socket.socket()        
 
# Define the port on which you want to connect
port = 6669             
 
# connect to the server on local computer
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect(('10.0.0.95', port))
 
while(True):
    print (s.recv(1024).decode())
