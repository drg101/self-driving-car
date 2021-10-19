import RPi.GPIO as GPIO
import time
import threading
import numpy as np
import math
from control import setSpeed

class SpeedEncoder:
    def __init__(self, size=6, laserGPIOPin=22, goalRPM=250):
        print("I AM HERE")
        self.size = size
        self.index = 0
        self.laser = laserGPIOPin
        self.previousTicks = np.array([i for i in range(size)])
        self.previousTicks = self.previousTicks.astype('float64')

        self.acceptedRPMs = np.array([0 for i in range(size)])
        self.acceptedRPMIndex = 0

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
                newSpeed = min(max(math.floor(30 - (avgRpm - self.goal) / 5),0),100)
                print(newSpeed)
                setSpeed(newSpeed)
            else:
                setSpeed(50)
            time.sleep(1/10)

    def getSmoothedCurrentRPM(self):
        return math.floor(np.mean(np.sort(self.acceptedRPMs)[:(self.size // 2)]))

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
            if time.time() - lastRPMSetTime > 1:
                reflect = 0

            if reflect != oldReflect:
                if reflect == 0:
                    up+=1
                    lastRPMSetTime = time.time()
                    self.previousTicks[self.index] = time.time()
                    self.index += 1
                    self.index = self.index % self.size

                oldReflect = reflect

    def getAvgRPM(self):
        sortedSpeed = np.sort(self.previousTicks)
        diffs = np.diff(sortedSpeed)
        # print('diffs')
        # print(diffs)
        rpms = 60 / diffs
        # print('rpm')
        # print(rpms)
        mean = np.mean(rpms)
        return mean
