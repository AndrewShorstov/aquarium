import machine
import config

class Pump:
    def __init__(self, pin1):
        self._pin1 = machine.Pin(pin1, machine.Pin.OUT, value = 0)
        self._status = config.PUMP_OFF_LABEL
        
        
    def on(self):
        self._pin1.value(1)
        self._status = config.PUMP_ON_LABEL


    def off(self):
        self._pin1.value(0)
        self._status = config.PUMP_OFF_LABEL


    def status(self):
        return self._status

