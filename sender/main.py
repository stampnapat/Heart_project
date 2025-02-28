import espnow
import json
import network
import utime

from machine import Pin, ADC

wifi = network.WLAN(network.WLAN.IF_STA)
wifi.active(True)

e = espnow.ESPNow()
e.active(True)
peer = b'\xf4\x12\xfa\xe8\xa3\x88'
e.add_peer(peer)

button = Pin(2, Pin.IN, Pin.PULL_UP)
ldr = ADC(Pin(4, Pin.IN))
ldr.atten(ADC.ATTN_11DB)

while True:
    data = json.dumps({"button": button.value() == 0, "ldr": ldr.read()})
    e.send(peer, data)
    utime.sleep_ms(100)

