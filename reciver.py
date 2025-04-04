from machine import Pin, I2C, ADC, SoftI2C
import ssd1306
import random
from time import sleep
import time
import framebuf
import math
import network
import espnow
import math
import json
from machine import Timer, Pin, PWM
from umqtt.simple import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS,
    TOPIC_PREFIX
)

#PORT 9

#######------------------------Set-Up--------------------------#####################
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
esp = espnow.ESPNow()
esp.active(True)

red = Pin(42, Pin.OUT)
yellow = Pin(41, Pin.OUT)
green = Pin(40, Pin.OUT)
sw = Pin(2, Pin.IN, Pin.PULL_UP)

i2c = SoftI2C(sda=Pin(48), scl=Pin(47))
display = ssd1306.SSD1306_I2C(128, 64, i2c)
adc = ADC(Pin(4))
adc.atten(ADC.ATTN_11DB)

mic = ADC(Pin(4))
mic.atten(ADC.ATTN_11DB)
dB_max = 50
peak_dB = 0

graph_data_hr = [32] * 128
graph_data_sound = [32] * 64

buzzer = PWM(Pin(5))
zone = ""
change_zone = [True,zone]
              
#########----------------------------mqtt------------------------------------##########

TOPIC_HR = f'{TOPIC_PREFIX}/HR'
TOPIC_MIC = f'{TOPIC_PREFIX}/MIC'
TOPIC_IR = f'{TOPIC_PREFIX}/IR'
TOPIC_OLED = f'{TOPIC_PREFIX}/OLED'
TOPIC_BUZZER = f'{TOPIC_PREFIX}/BUZZER'



mqtt = MQTTClient(client_id='',
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)


def connect_wifi():
    mac = ':'.join(f'{b:02X}' for b in wifi.config('mac'))
    print(f'WiFi MAC address is {mac}')
    wifi.active(True)
    print(f'Connecting to WiFi {WIFI_SSID}.')
    wifi.connect(WIFI_SSID, WIFI_PASS)             
    while not wifi.isconnected():
        print('.', end='')
        sleep(0.5)
    print('\nWiFi connected.')
    
def mqtt_callback(T, msg):
    global status_oled,status_buzzer
    print(type(T),type(msg),msg,T)
    payload = int(msg)
    topic = T.decode()
    if  topic == TOPIC_OLED:
        if payload ==1:
            status_oled = "ON"
        elif payload == 0:
            status_oled = "OFF" 
    if topic == TOPIC_BUZZER:
        if payload ==1:
            status_buzzer = "ON"
        elif payload == 0:
            status_buzzer = "OFF"
    
    
def connect_mqtt():
    print(f'Connecting to MQTT broker at {MQTT_BROKER}.')
    mqtt.connect()
    mqtt.set_callback(mqtt_callback)
    mqtt.subscribe(TOPIC_OLED)
    mqtt.subscribe(TOPIC_BUZZER)
    print('MQTT broker connected.')



        


############################################################----sound----########
        

def playsound_happy():
    global buzzer 
    notes = {
        "C4": 261, "D4": 520, "E4": 330, "F4": 349, "G4": 392,
        "A4": 440, "B4": 494 , "F":800 , "A": 850
    }

    melody = [("F", 0.1),("A", 0.1)]

    for note, duration in melody:
        buzzer.freq(notes[note])
        buzzer.duty(100)
        time.sleep(duration)
        buzzer.duty(0) 
        time.sleep(0.1) 

    
    
    
def playsound_normal():
    global buzzer 
    buzzer = PWM(Pin(5))
    notes = {
        "C4": 261, "D4": 520, "E4": 330, "F4": 349, "G4": 392,
        "A4": 440, "B4": 494
    }

    melody = [("C4", 0.2),("D4", 0.2)]

    for note, duration in melody:
        buzzer.freq(notes[note])
        buzzer.duty(512)
        time.sleep(duration) 
        buzzer.duty(0) 
        time.sleep(0.1)


def playsound_scary():
    global buzzer 
    buzzer = PWM(Pin(5))
    notes = {
        "C4": 261, "D4": 520, "E4": 250, "F4": 220, "G4": 100,
        "A4": 440, "B4": 494
    }

    melody = [("E4", 0.2), ("F4", 0.2),("G4", 0.3)]

    for note, duration in melody:
        buzzer.freq(notes[note])
        buzzer.duty(500) 
        time.sleep(duration) 
        buzzer.duty(0) 
        time.sleep(0.1)


def playsound_shock():
    global buzzer 
    buzzer = PWM(Pin(5))
    notes = {
        "C4": 261, "D4": 520, "E4": 700, "F4": 220, "G4": 100,
        "A4": 440, "B4": 494
    }

    melody = [("E4", 0.2), ("E4", 0.2),("E4", 0.2),("E4", 0.2),("E4", 0.2)]

    for note, duration in melody:
        buzzer.freq(notes[note])
        buzzer.duty(500) 
        time.sleep(duration)
        buzzer.duty(0) 
        time.sleep(0.1)

#########################-----------oled-----------#################################

def graph_hr(hr, name, a):
    global graph_data_hr
    display.fill(0)
    if hr >= 20000:
        pixel_value = int(63 - ((hr - 28000) * 63 / (33000 - 28000)))

        pixel_value = max(0, min(63, pixel_value))

        graph_data_hr.pop(0)
        graph_data_hr.append(pixel_value)
        
        for x in range(1, 127):
            display.line(x - 1, graph_data_hr[x - 1], x, graph_data_hr[x], 1)

        display.text(f'{name}: {a}', 0, 2, 1)
        display.show()
    else:
        text = "NO FINGER"
        text_x = (display.width - len(text) * 8) // 2
        text_y = (display.height // 2) - 4
        display.fill(0)
        display.text(text, text_x, text_y, 1)
        display.show()



def graph_sound(hr, sound_value, name):
    global graph_data_sound
    display.fill(0)
    if hr >= 20000:
        db_value = int(((sound_value - 120) * 63) / (150 - 120))
        db_value = max(0, min(db_value, 63))

        if len(graph_data_sound) >= 63:
            graph_data_sound.pop(0)
        graph_data_sound.append(db_value)

        for x in range(1, len(graph_data_sound)):
            display.line(x - 1, 64 - graph_data_sound[x - 1], x, 64 - graph_data_sound[x], 1)

        display.text(f'{name}: {sound_value} ', 0, 2, 1)
        display.show()
    else:
        text = "NO FINGER"
        text_x = (display.width - len(text) * 8) // 2
        text_y = (display.height // 2) - 4
        display.fill(0)
        display.text(text, text_x, text_y, 1)
        display.show()
        
        
        
def draw_emote(hr, emote, x_offset=20, y_offset=5):
    display.fill(0)
    if hr >= 20000:
        for y, row in enumerate(emote):
            for x, pixel in enumerate(row):
                if pixel == "X":
                    for dy in range(SCALE):
                        for dx in range(SCALE):
                            display.pixel(x * SCALE + dx + x_offset, y * SCALE + dy + y_offset, 1)
        display.show()
    else:
        text = "NO FINGER"
        text_x = (display.width - len(text) * 8) // 2
        text_y = (display.height // 2) - 4
        display.fill(0)
        display.text(text, text_x, text_y, 1)
        display.show()


normal_face = [
    "       XXXXXXX       ",
    "      X       X      ",
    "     X         X     ",
    "    X           X    ",
    "    X           X    ",
    "   X             X   ",
    "   X             X   ",
    "  X     X   X     X  ",
    "  X               X  ",
    "   X             X   ",
    "   X    XXXXX    X   ",
    "    X           X    ",
    "     X         X     ",
    "      X       X      ",
    "       XXXXXXX       "
]
happy_face = [
    "       XXXXXXX       ",
    "      X       X      ",
    "     X         X     ",
    "    X           X    ",
    "    X           X    ",
    "   X             X   ",
    "   X             X   ",
    "  X     X   X     X  ",
    "  X               X  ",
    "   X   X     X   X   ",
    "   X    XXXXX    X   ",
    "    X           X    ",
    "     X         X     ",
    "      X       X      ",
    "       XXXXXXX       "
]
scared_face = [
    "       XXXXXXX       ",
    "      X       X      ",
    "     X         X     ",
    "    X  XX   XX  X    ",
    "    X X  X X  X X    ",
    "   X             X   ",
    "   X    X   X    X   ",
    "  X               X  ",
    "  X               X  ",
    "   X     XXX     X   ",
    "   X    XXXXX    X   ",
    "    X           X    ",
    "     X         X     ",
    "      X       X      ",
    "       XXXXXXX       "
]
SCALE = 4  

    
#####################---iqr-----############################################################
debounce_timer = Timer(0)
    
def mode_change(pin):
    global mode

    def debounce_callback(timer):
        global mode
        if pin.value() == 0: 
            mode = (mode + 1) % 3
            print("Click")

    debounce_timer.init(mode=Timer.ONE_SHOT, period=0, callback=debounce_callback)


sw.irq(trigger=Pin.IRQ_FALLING, handler=mode_change)
mode = 0

##############################################################################################3

buzzer.duty(0)

connect_wifi()
connect_mqtt()

counter = 0
topic = ""
payload = ""
status_buzzer ="ON"
status_oled ="ON"
sound_value = 0
########################################################---main-----#####################################33
while True:
    host, msg = esp.recv()
    mqtt.check_msg()
    if msg:
        dct = json.loads(msg.decode())
        redValue = dct["redValue"]
        irValue = dct["irValue"]
        heartrate = dct["heartrate"]
        avg = dct["avgHr"]
        old_sound = sound_value
        sound_value = dct["db"]
    #FOR DEDUG
#     redValue = random.randint(60, 120)
#     irValue = random.randint(60,120)
#     print(dct)
    #change mode
    if mode == 0:
        name = "heart rate"
        if status_oled =="ON":
            graph_hr(redValue, name,int(heartrate))
        elif status_oled =="OFF":
            display.fill(0)
            display.show()
            
            
    elif mode == 1:
        name = "sound"
        if status_oled =="ON":
            graph_sound(redValue, sound_value, name)
        elif status_oled =="OFF":
            display.fill(0)
            display.show()
            
            
    elif mode == 2:
        if status_oled =="ON":  
            if redValue <= 30000:
                draw_emote(redValue, happy_face)
            elif 30000 < redValue <= 32000:
                draw_emote(redValue, normal_face)
            elif redValue > 32000:
                draw_emote(redValue, scared_face)
        elif status_oled =="OFF":
            display.fill(0)
            display.show() 

        
    
    #status
    if abs(sound_value - old_sound) >= 20:
        zone = "shock"
        if change_zone[1] != zone:
            change_zone[1] = zone
            change_zone[0] = True
            
        if change_zone[0] == True:
            if status_buzzer =="ON" :
                 playsound_shock()
            change_zone[0] = False
    
    
    elif redValue <= 30000:
        zone = "happy"
        if change_zone[1] != zone:
            change_zone[1] = zone
            change_zone[0] = True
            
        if change_zone[0] == True:
            if status_buzzer =="ON" :
                    playsound_happy()
            change_zone[0] = False

        green.value(1)
        red.value(0)
        yellow.value(0)        


    elif 30000 < redValue < 32000:
        zone = "normal"
        if change_zone[1] != zone:
            change_zone[1] = zone
            change_zone[0] = True
            
        if change_zone[0] == True:
            if status_buzzer =="ON" :
                    playsound_normal()
            change_zone[0] = False
        green.value(0)
        red.value(0)
        yellow.value(1)


    elif redValue >= 32000:
        zone = "scared"
        if change_zone[1] != zone:
            change_zone[1] = zone
            change_zone[0] = True
            
        if change_zone[0] == True:
            if status_buzzer =="ON" :
                    playsound_scary()
            change_zone[0] = False    
            change_zone[0] = False
        green.value(0)
        red.value(1)
        yellow.value(0)

    else:
        zone = "not start"
    
#     print(f"Zone: {zone}, Mode: {mode}, Red: {redValue}, IR: {irValue}, dB:{sound_value}, oled: {status_oled}, buzzer: {status_buzzer}, current_paylod:{payload}")
#     print(counter)    
#     counter+=1
    mqtt.publish(TOPIC_HR, str(redValue))
    mqtt.publish(TOPIC_MIC, str(sound_value))

    sleep(0.2)

    








