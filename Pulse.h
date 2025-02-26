from machine import Pin, I2C
import time

MAX30105_ADDRESS = 0x57

# Register addresses
REG_INTR_STATUS_1 = 0x00
REG_INTR_STATUS_2 = 0x01
REG_INTR_ENABLE_1 = 0x02
REG_INTR_ENABLE_2 = 0x03
REG_FIFO_WR_PTR = 0x04
REG_OVF_COUNTER = 0x05
REG_FIFO_RD_PTR = 0x06
REG_FIFO_DATA = 0x07
REG_FIFO_CONFIG = 0x08
REG_MODE_CONFIG = 0x09
REG_SPO2_CONFIG = 0x0A
REG_LED1_PA = 0x0C
REG_LED2_PA = 0x0D
REG_PILOT_PA = 0x10
REG_MULTI_LED_CTRL1 = 0x11
REG_MULTI_LED_CTRL2 = 0x12
REG_TEMP_INTR = 0x1F
REG_TEMP_FRAC = 0x20
REG_TEMP_CONFIG = 0x21
REG_PROX_INT_THRESH = 0x30
REG_REV_ID = 0xFE
REG_PART_ID = 0xFF

NSAMPLE = 24
NSLOT = 4

class MAFilter:
    def __init__(self):
        self.buffer = [0] * NSLOT
        self.nextslot = 0

    def filter(self, value):
        self.buffer[self.nextslot] = value
        self.nextslot = (self.nextslot + 1) % NSLOT
        return sum(self.buffer) // NSLOT

class DCFilter:
    def __init__(self):
        self.sample_avg_total = 0

    def filter(self, sample):
        self.sample_avg_total += (sample - self.sample_avg_total // NSAMPLE)
        return sample - self.sample_avg_total // NSAMPLE

    def avgDC(self):
        return self.sample_avg_total // NSAMPLE

class Pulse:
    def __init__(self):
        self.dc = DCFilter()
        self.ma = MAFilter()
        self.amplitude_avg_total = 0
        self.cycle_max = 0
        self.cycle_min = 0
        self.positive = False
        self.prev_sig = 0

    def dc_filter(self, sample):
        return self.dc.filter(sample)

    def ma_filter(self, sample):
        return self.ma.filter(sample)

    def isBeat(self, signal):
        return abs(signal - self.prev_sig) > 2000

    def avgDC(self):
        return self.dc.avgDC()

    def avgAC(self):
        return self.amplitude_avg_total // 4

sensor = MAX30102(scl=10, sda=9)  # Adjust pins according to your ESP32-S3 board
sensor.setup()
time.sleep(1)

while True:
    if sensor.check():
        red, ir = sensor.read_fifo_sample()
        red_filtered = sensor.dc_filter(red)
        ir_filtered = sensor.dc_filter(ir)
        red_smoothed = sensor.ma_filter(red_filtered)
        ir_smoothed = sensor.ma_filter(ir_filtered)
        print("Red:", red_smoothed, "IR:", ir_smoothed)
    time.sleep(0.1)

