"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display
This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import time

global oled
global image
global draw
global font

def oled_init():
    global oled
    global image
    global draw
    global font
    # Display size
    WIDTH = 128
    HEIGHT = 64
    BORDER = 5

    # I2C.
    i2c = board.I2C()
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

    # Clear display.
    oled.fill(0)
    oled.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Load default font.
    font = ImageFont.truetype('rpi-lib/Font.ttf', 16)

    # Draw Some Text
    text = "Sea-Picro Tester"
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )

    # Display image
    oled.image(image)
    oled.show()

def oled_write(text, size=16):
    global oled
    global image
    global draw
    global font

    # Clear display.
    oled.fill(0)
    oled.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Load default font.
    font = ImageFont.truetype('rpi-lib/Font.ttf', size)

    # Draw Some Text
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (oled.width // 2 - font_width // 2, oled.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )

    # Display image
    oled.image(image)
    oled.show()

def oled_write_dual(text1, text2, size1=20, size2=20):
    global oled
    global image
    global draw
    global font

    # Clear display.
    oled.fill(0)
    oled.show()

    # Create blank image for drawing.
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new("1", (oled.width, oled.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Load default font.
    font1 = ImageFont.truetype('rpi-lib/Font.ttf', size1)
    font2 = ImageFont.truetype('rpi-lib/Font.ttf', size2)

    # Draw Some Text
    (font_width, font_height) = font.getsize(text1)
    draw.text(
        (oled.width // 2 - font_width // 2 - 15, oled.height // 2 - font_height // 2 - 20),
        text1,
        font=font1,
        fill=255,
    )
    (font_width, font_height) = font.getsize(text2)
    draw.text(
        (oled.width // 2 - font_width // 2 + 10, oled.height // 2 - font_height // 2 + 20),
        text2,
        font=font2,
        fill=255,
    )
    # Display image
    oled.image(image)
    oled.show()