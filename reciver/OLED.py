from machine import Pin, I2C

import ssd1306

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

def clear_oled(oled):
    oled.fill(0)
    oled.show()

def draw_emote(oled, emote, x_offset=20, y_offset=5):
    oled.fill(0)  # ล้างหน้าจอ
    for y, row in enumerate(emote):
        for x, pixel in enumerate(row):
            if pixel == "X":
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        oled.pixel(x * SCALE + dx + x_offset, y * SCALE + dy + y_offset, 1)
    oled.show()

