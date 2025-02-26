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

class MAX30102:
    def __init__(self, scl=22, sda=21, i2c_freq=400000):
        self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=i2c_freq)
        self.address = MAX30105_ADDRESS

    def write_register(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def read_register(self, reg, num_bytes=1):
        return self.i2c.readfrom_mem(self.address, reg, num_bytes)

    def setup(self):
        self.write_register(REG_MODE_CONFIG, 0x03)  # SpO2 mode
        self.write_register(REG_SPO2_CONFIG, 0x27)  # Sample rate: 100 Hz, Pulse Width: 411us
        self.write_register(REG_LED1_PA, 0x1F)      # Red LED Power
        self.write_register(REG_LED2_PA, 0x1F)      # IR LED Power

    def check(self):
        return self.read_register(REG_INTR_STATUS_1)[0]

    def read_fifo_sample(self):
        data = self.read_register(REG_FIFO_DATA, 6)
        red = (data[0] << 16) | (data[1] << 8) | data[2]
        ir = (data[3] << 16) | (data[4] << 8) | data[5]
        return red, ir

# Example Usage
sensor = MAX30102(scl=10, sda=9)  # Adjust pins according to your ESP32-S3 board
sensor.setup()
time.sleep(1)

while True:
    if sensor.check():
        red, ir = sensor.read_fifo_sample()
        print("Red:", red, "IR:", ir)
    time.sleep(0.1)

