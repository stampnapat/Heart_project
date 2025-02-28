import espnow
import json
import network
import utime

from machine import Pin, I2C

import ssd1306

from OLED import *

i2c = I2C(0, scl=Pin(47), sda=Pin(48))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

clear_oled(oled)

wifi = network.WLAN(network.WLAN.IF_STA)
wifi.active(True)

e = espnow.ESPNow()
e.active(True)

while True:
    host, msg = e.irecv()
    json_msg = json.loads(msg.decode())
    print(json_msg)
    if "button" in json_msg:
        if json_msg["button"]:
            clear_oled(oled)
            utime.sleep(1)
            
    if "ldr" in json_msg:
        ldr_val = json_msg["ldr"]
        if ldr_val < 1000:
            draw_emote(oled, happy_face)
        elif ldr_val <  2000:
            draw_emote(oled, normal_face)
        else:
            draw_emote(oled, scared_face)
        
    

