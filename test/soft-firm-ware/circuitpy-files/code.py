# General Imports  
import board
import digitalio
import time

# Neopixel LED
import neopixel
from rainbowio import colorwheel

# USB Serial
import usb_cdc
serial = usb_cdc.data
if serial is None:
    print("Need to enable USB CDC serial data in boot.py.")
    while True:
        pass

# Function to print to CDC data not CDC REPL
def serial_print(string):
    serial.write("{}\r\n".format(string).encode())

# Init LED
led = neopixel.NeoPixel(board.NEOPIXEL, 1)
led.brightness = 0.1
j = 0

# LED states for testing
led_state = 0
LED_OFF = 0
LED_RED = 1
LED_GRN = 2
LED_BLU = 3
LED_RGB = 4
LED_RBW = 5

# IO Pins to be tested
io_test_pins_init = [board.D0, board.D1, board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9, board.D21, board.D23, board.D20, board.D22, board.D26, board.D27, board.D28, board.D29, board.D12, board.D13, board.D14, board.D15, board.D16]
# Array to store configured pins
io_test_pins = []

# VBUS detect pin
vbus_pin = digitalio.DigitalInOut(board.D19)
vbus_pin.direction = digitalio.Direction.INPUT
vbus_pin.pull = digitalio.Pull.DOWN

# Make all test pins inputs with pullups
for pin in io_test_pins_init :
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.UP
    io_test_pins.append(key_pin)

while True:
    # Check if we have a message waiting for us on UART
    if serial.in_waiting > 0:
        rx_msg = serial.readline().decode()[0:-2] # Convert from byte array and strip \r\n

        if rx_msg == "ident":
            serial_print("ident = Sea-Picro!")

        elif rx_msg == "vbus_test":
            vbus_state = vbus_pin.value
            if (vbus_state):
                serial_print("vbus = high")
            else:
                serial_print("vbus = low")

        elif rx_msg == "io_test":
            io_test_pins_val = []
            for pin in io_test_pins:
                io_test_pins_val.append(not pin.value)
            serial_print(io_test_pins_val)            

        elif rx_msg == "led_off":
            led_state = LED_OFF
        elif rx_msg == "led_red":
            led_state = LED_RED
        elif rx_msg == "led_grn":
            led_state = LED_GRN
        elif rx_msg == "led_blu":
            led_state = LED_BLU
        elif rx_msg == "led_rgb":
            led_state = LED_RGB
        elif rx_msg == "led_rbw":
            led_state = LED_RBW

        else:
            print("Unknown RX MSG: " + rx_msg)

    if led_state == LED_OFF:
        led.fill((0,0,0))
    elif led_state == LED_RED:
        led.fill((255,0,0))
    elif led_state == LED_GRN:
        led.fill((0,255,0))
    elif led_state == LED_BLU:
        led.fill((0,0,255))
    elif led_state == LED_RGB:
        led.fill((255,0,0))
        time.sleep(0.5)
        led.fill((0,255,0))
        time.sleep(0.5)
        led.fill((0,0,255)) 
        time.sleep(0.5)
    elif led_state == LED_RBW:
        j = (j + 1) % 256 
        led.fill(colorwheel(j))
        time.sleep(0.01)