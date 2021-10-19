import RPi.GPIO as GPIO
import time

fw = 23
bk = 24

leftP = 20
rightP = 21
turnStrengthP = 16

speed = 50

# global for the current fore-aft control
fwC = 0

# pwm frequency. 
pwmHz = 440

GPIO.setmode(GPIO.BCM)
GPIO.setup(fw,GPIO.OUT)
GPIO.setup(bk,GPIO.OUT)
GPIO.setup(leftP,GPIO.OUT)
GPIO.setup(rightP,GPIO.OUT)
GPIO.setup(turnStrengthP,GPIO.OUT)

fwS=GPIO.PWM(fw,pwmHz)
fwS.start(0)
bkS=GPIO.PWM(bk,pwmHz)
bkS.start(0)
turnS=GPIO.PWM(turnStrengthP,1000)
turnS.start(100)
# GPIO.output(fw,GPIO.LOW)
# GPIO.output(bk,GPIO.LOW)

GPIO.output(leftP,GPIO.LOW)
GPIO.output(rightP,GPIO.LOW)

def setSpeed(x):
    '''0<=x<=100'''
    global speed
    speed = x
    if fwC == 1:
        fwS.ChangeDutyCycle(speed)
    elif fwC == -1:
        bkS.ChangeDutyCycle(speed)

def forward():
    print("fw")
    global fwC
    fwC = 1
    bkS.ChangeDutyCycle(0)
    fwS.ChangeDutyCycle(speed)
    # GPIO.output(bk, GPIO.LOW)
    # GPIO.output(fw, GPIO.HIGH)

def backward():
    print("bk")
    global fwC
    fwC = -1
    fwS.ChangeDutyCycle(0)
    bkS.ChangeDutyCycle(speed)
    # GPIO.output(fw, GPIO.LOW)
    # GPIO.output(bk, GPIO.HIGH)

def stop():
    print("stop")
    global fwC
    fwC = 0
    bkS.ChangeDutyCycle(0)
    fwS.ChangeDutyCycle(0)
    # GPIO.output(fw, GPIO.LOW)
    # GPIO.output(bk, GPIO.LOW)

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

