from machine import Pin
from time import sleep_ms, sleep_us

class Stepper:
    FULL_STEP, HALF_STEP = ((0,4), (1,8))
    FULL_ROUND = 2048
    MAX_SPEED = 200
    _TABLE = (((1,1,0,0),(0,1,1,0),(0,0,1,1),(1,0,0,1)),                                         # Full step
              ((1,0,0,0),(1,1,0,0),(0,1,0,0),(0,1,1,0),(0,0,1,0),(0,0,1,1),(0,0,0,1),(1,0,0,1))) # Half step
    def __init__(self, orange, yellow, pink, blue):
        self._pin = [ Pin(pin, Pin.OUT) for pin in (orange, yellow, pink, blue) ]
        self._speed = self.MAX_SPEED
        self._mode = self.FULL_STEP
        self._step = 0
    
    def _oneStep(self):
        for i,pin in enumerate(self._pin):
            pin.value(self._TABLE[self._mode[0]][(self._step)%self._mode[1]][i])
            sleep_us(self._speed)
        self._step = self._step+1

    
    def _relax(self):
        for pin in self._pin:
            pin.value(0)
        
    def setMode(self, mode):
        if mode in (self.FULL_STEP, self.HALF_STEP):
            self._mode = mode
    
    def setSpeed(self, speed):
        if (speed < self.MAX_SPEED):
            return
        self._speed = speed
    
    def step(self, times = 1):
        if (times < 1):
            return
        for _ in range(times):
            self._oneStep()
        self._relax()
        
    def fullRound(self):
        for _ in range(self.FULL_ROUND):
            self._oneStep()
        self._relax()
