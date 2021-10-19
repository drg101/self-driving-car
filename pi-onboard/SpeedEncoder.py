import RPi.GPIO as GPIO
import time
import threading
import numpy as np
import math
from control import setSpeed

class SpeedEncoder:
    def __init__(self, tickrate=4, laserGPIOPin=22, goalRPM=90):
        print("I AM HERE")
        self.laser = laserGPIOPin
        self.goal = goalRPM
        self.tickrate = tickrate
        self.currentSpeed = 0
        self.currentPower = 0
        setSpeed(self.currentPower)

        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(self.laser, GPIO.IN)
        self.startPolling()
    
    def updatePower(self):
        setSpeed(self.currentPower)

    def startPolling(self):
        threading.Thread(target=self.poll, args=[]).start()
        return self

    def poll(self):
        print("starting polling for speed!")
        oldReflect = 1
        lastFlush = time.time()
        lastTickTime = 0
        currentTickCount = 0
        lastSpeed = 0
        while 1:
            reflect = GPIO.input(self.laser)
            if reflect != oldReflect:
                rpm = 15 / (time.time() - lastTickTime)
                if reflect == 0 and rpm < 500:
                    # print(f'Caught rpm@{rpm}')
                    lastTickTime = time.time()
                    currentTickCount += 1
                oldReflect = reflect
            if time.time() - lastFlush > (1/self.tickrate):
                self.currentSpeed = currentTickCount * 15 * self.tickrate
                print(f'speed:{self.currentSpeed}')
                lastSpeed = self.currentSpeed
                if self.currentSpeed == 120:
                    self.currentPower = 33
                if self.currentSpeed == 0 and lastSpeed == 0:
                    self.currentPower = 70
                if self.currentSpeed == 0 and lastSpeed > 0:
                    self.currentPower = 40
                if self.currentSpeed > 120 and lastSpeed > 120:
                    self.currentPower = 20
                if self.currentSpeed < 120 and lastSpeed >= 120:
                    self.currentPower = 44
                if self.currentSpeed > 0 and self.currentSpeed < 120 and lastSpeed < 120 and lastSpeed > 0:
                    self.currentPower = 53
                # self.currentPower = max(0,min(100,self.currentPower))
                print(self.currentPower)
                lastFlush = time.time()
                currentTickCount = 0
                self.updatePower()

