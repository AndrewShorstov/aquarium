import machine
import config

class Lamp:
    def __init__(self, pin1, pin2):
        self._pin1 = machine.Pin(pin1, machine.Pin.OUT, value = 0)
        self._pin2 = machine.Pin(pin2, machine.Pin.OUT, value = 0)
        self._status = config.OFFLIGHT_LABEL 
    
    def daylight(self):
        self._pin2.value(0)
        self._pin1.value(1)
        self._status = config.DAYLIGHT_LABEL 
    
    
    def nightlight(self):
        self._pin1.value(0)
        self._pin2.value(1)
        self._status = config.NIGHTLIGHT_LABEL 
    

    def offlight(self):
        self._pin1.value(0)
        self._pin2.value(0)
        self._status = config.OFFLIGHT_LABEL 


    def status(self):
        return self._status