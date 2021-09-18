import RPi.GPIO as GPIO
import time

fw = 23
bk = 24

leftP = 20
rightP = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(fw,GPIO.OUT)
GPIO.setup(bk,GPIO.OUT)
GPIO.setup(leftP,GPIO.OUT)
GPIO.setup(rightP,GPIO.OUT)

GPIO.output(fw,GPIO.LOW)
GPIO.output(bk,GPIO.LOW)
GPIO.output(leftP,GPIO.LOW)
GPIO.output(rightP,GPIO.LOW)

def setSpeed(x):
    '''0<=x<=100'''
    # print(f"speed set to {x}")
    # p.ChangeDutyCycle(x) 
    return

def forward():
    print("fw")
    GPIO.output(bk, GPIO.LOW)
    GPIO.output(fw, GPIO.HIGH)

def backward():
    print("bk")
    GPIO.output(fw, GPIO.LOW)
    GPIO.output(bk, GPIO.HIGH)

def stop():
    print("stop")
    GPIO.output(fw, GPIO.LOW)
    GPIO.output(bk, GPIO.LOW)

def left():
    print("left")
    GPIO.output(rightP, GPIO.LOW)
    GPIO.output(leftP, GPIO.HIGH)

def right():
    print("right")
    GPIO.output(leftP, GPIO.LOW)
    GPIO.output(rightP, GPIO.HIGH)

def straight():
    print("straight")
    GPIO.output(leftP, GPIO.LOW)
    GPIO.output(rightP, GPIO.LOW)

if __name__ == "__main__":
    initSpeed = 10
    while True:
        initSpeed += 10
        setSpeed(initSpeed % 100)
        forward()
        left()
        time.sleep(1)
        backward()
        right()
        time.sleep(1)
        stop()
        straight()
        time.sleep(1)

