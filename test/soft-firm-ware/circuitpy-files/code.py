import time

import board
import digitalio
import neopixel
from rainbowio import colorwheel
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# Pinout order is around the normal pro micro pins anticlockwise, then the Elite-C pins anticlockwise. Maps to A->Z
keypress_pins = [board.D0,  board.D1,   board.D2,   board.D3,   board.D4,   board.D5,   board.D6,   board.D7,   board.D8,   board.D9,   board.D21, board.D23, board.D20, board.D22, board.D26, board.D27, board.D28, board.D29, board.D12,  board.D13,  board.D14,  board.D15,  board.D16]
keys_pressed =  [Keycode.A, Keycode.B,  Keycode.C,  Keycode.D,  Keycode.E,  Keycode.F,  Keycode.G,  Keycode.H,  Keycode.I,  Keycode.J,  Keycode.K, Keycode.L, Keycode.M, Keycode.N, Keycode.O, Keycode.P, Keycode.Q, Keycode.R, Keycode.S,  Keycode.T,  Keycode.U,  Keycode.V,  Keycode.W]

key_pin_array = []

keyboard = Keyboard(usb_hid.devices)

# Make all pins inputs with pullups
for pin in keypress_pins:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.UP
    key_pin_array.append(key_pin)

# Init rainbow LED whilst we wait for testing
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.3
j = 0

while True:
    # Check each pin
    for key_pin in key_pin_array:
        if not key_pin.value:               # Check if pin is grounded
            i = key_pin_array.index(key_pin)

            while not key_pin.value:        # Wait for it to be ungrounded
                pass
            keyboard.send(keys_pressed[i])  # With key released, send key's keycode
            keyboard.send(Keycode.ENTER)    # Hit enter so the test script process the keypress
            time.sleep(0.01)                # Hold key for 10ms
            keyboard.release_all()          # Release all keys

    # Fade LED colours whilst we test
    j = (j + 1) % 256
    led.fill(colorwheel(j))
    time.sleep(0.01)


