import RPi.GPIO as GPIO
import time
import threading
import numpy as np
import math
from control import setSpeed

class SpeedEncoder:
    def __init__(self, size=4, laserGPIOPin=22, goalRPM=350):
        print("I AM HERE")
        self.size = size
        self.index = 0
        self.laser = laserGPIOPin
        self.previousTicks = np.array([i for i in range(size)])
        self.previousTicks = self.previousTicks.astype('float64')

        
        self.isStopped = False
        self.lastRPM = 0

        self.goal = goalRPM

        GPIO.setmode(GPIO.BCM)  
        GPIO.setup(self.laser, GPIO.IN)
        setSpeed(100)
        self.startPolling()
        self.startControllingSpeed()
    
    def startControllingSpeed(self):
        threading.Thread(target=self.controlSpeed, args=[]).start()
        return self

    def controlSpeed(self):
        while 1:
            avgRpm = self.getAvgRPM()
            print(f'avgRpm = {avgRpm}')
            if avgRpm != self.goal:
                newSpeed = min(max(math.floor(40 - (avgRpm - self.goal) / 4),0),100)
                # if self.isStopped:
                #     newSpeed = 100
                print(f'newspeed = {newSpeed}')
                setSpeed(newSpeed)
            else:
                setSpeed(50)
            time.sleep(1/60)

    def startPolling(self):
        threading.Thread(target=self.poll, args=[]).start()
        return self

    def poll(self):
        print("starting polling for speed!")
        oldReflect = 1
        oldTime = 0
        up = 0
        lastRPMSetTime = 0
        while 1:
            reflect = GPIO.input(self.laser)
            falseKick = False
            if time.time() - lastRPMSetTime > 0.2:
                falseKick = True

            if reflect != oldReflect or falseKick:
                if reflect == 0 or falseKick:
                    up+=1
                    rpm = 60 / (time.time() - lastRPMSetTime) 
                    if rpm > 760:
                        continue
                    if falseKick:
                        self.isStopped = True
                        rpm = 0
                    else:
                        self.isStopped = False
                    self.previousTicks[self.index] = rpm
                    self.index += 1
                    self.index = self.index % self.size
                    self.lastRPM = rpm
                    lastRPMSetTime = time.time()

                oldReflect = reflect

    def getAvgRPM(self):
        mean = np.mean(self.previousTicks)
        return mean
