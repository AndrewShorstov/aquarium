try:
    import usocket as socket
except:
    import socket

from machine import Pin
from time import sleep_ms
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'A.I.SH'
password = '3D$OIhtRn'

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

led = Pin(2, Pin.OUT)
state = int(1)
while station.isconnected() == False:
  led.value(state&1)
  sleep_ms(200)
  state = state + 1

led.value(0)

print('Connection successful')
print(station.ifconfig())



