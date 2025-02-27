from machine import Pin, I2C
import ssd1306
import time

# ตั้งค่า I2C (เปลี่ยนขา GPIO ได้ถ้าจำเป็น)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# ตั้งค่า OLED Display
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# ล้างจอ
oled.fill(0)

# อารมณ์ (16x16 Pixel Art)
normal_face = [
    "        XX        ",
    "       X  X       ",
    "      X    X      ",
    "     X      X     ",
    "    X  X  X  X    ",
    "   X    XX    X   ",
    "   X          X   ",
    "  X    X  X    X  ",
    "  X          X  X ",
    "   X  X    X  X   ",
    "   X          X   ",
    "    X XXXXXX X    ",
    "     X      X     ",
    "      X    X      ",
    "       X  X       ",
    "        XX        "
]

frown_face = [
    "        XX        ",
    "       X  X       ",
    "      X    X      ",
    "     X      X     ",
    "    X  X  X  X    ",
    "   X    XX    X   ",
    "   X          X   ",
    "  X    X  X    X  ",
    "  X          X  X ",
    "   X  X    X  X   ",
    "   X          X   ",
    "    X  XXXX  X    ",
    "     X XXXX X     ",
    "      X    X      ",
    "       X  X       ",
    "        XX        "
]

confound_face = [
    "        XX        ",
    "       X  X       ",
    "      X    X      ",
    "     X XX  XX     ",
    "    X        X    ",
    "   X  X    X  X   ",
    "   X          X   ",
    "  X    X  X    X  ",
    "  X          X  X ",
    "   X  X    X  X   ",
    "   X          X   ",
    "    X  XXXX  X    ",
    "     X      X     ",
    "      X    X      ",
    "       X  X       ",
    "        XX        "
]

# ฟังก์ชันแสดงอารมณ์
def draw_emote(emote, x_offset=40, y_offset=20):
    oled.fill(0)  # ล้างหน้าจอ
    for y, row in enumerate(emote):
        for x, pixel in enumerate(row):
            if pixel == "X":
                oled.pixel(x + x_offset, y + y_offset, 1)  # วาดพิกเซล
    oled.show()

# วนลูปแสดงอารมณ์
while True:
    draw_emote(normal_face)   # 😐 Normal
    time.sleep(2)

    draw_emote(frown_face)    # 😠 Frown
    time.sleep(2)

    draw_emote(confound_face) # 🤨 Confound
    time.sleep(2)

