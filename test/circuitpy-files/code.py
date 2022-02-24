import time

import board
import digitalio
import neopixel
from rainbowio import colorwheel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# The pins we'll use, each will have an internal pullup
keypress_pins = [board.D0, board.D1, board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9, board.D21, board.D23, board.D20, board.D22, board.D26, board.D27, board.D28, board.D29]
# Our array of key objects
key_pin_array = []
keys_pressed = [Keycode.A, Keycode.B, Keycode.C, Keycode.D, Keycode.E, Keycode.F, Keycode.G, Keycode.H, Keycode.I, Keycode.J, Keycode.K, Keycode.L, Keycode.M, Keycode.N, Keycode.O, Keycode.P, Keycode.Q, Keycode.R]

keyboard = Keyboard(usb_hid.devices)

# Make all pin objects inputs with pullups
for pin in keypress_pins:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.UP
    key_pin_array.append(key_pin)


# Pretty LED whilst we wait for testing
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.3
j = 0

while True:
    # Check each pin
    for key_pin in key_pin_array:
        if not key_pin.value:  # Is it grounded?
            i = key_pin_array.index(key_pin)

            while not key_pin.value:
                pass  # Wait for it to be ungrounded!
            keyboard.send(keys_pressed[i])
            keyboard.send(Keycode.ENTER)
            time.sleep(0.01)
            keyboard.release_all()

    j = (j + 1) % 256  # run from 0 to 255
    led.fill(colorwheel(j))
    time.sleep(0.01)


