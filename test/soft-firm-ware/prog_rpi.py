#!/usr/bin/python

import RPi.GPIO as GPIO
import time
from adc import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Output LEDs, active low
LED_RED     = 12
LED_GREEN   = 13

GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.HIGH)

# Push buttons for user input, active high
SW_PASS     = 4
SW_FAIL     = 5

GPIO.setup(SW_PASS, GPIO.IN)
GPIO.setup(SW_FAIL, GPIO.IN)

# Slide switches for mode select
SW_EXT_RST  = 8     # HIGH = EXT, LOW = RST
SW_BOOTLD   = 9     # HIGH = YES, LOW = NO
SW_FIRMWARE = 10    # HIGH = YES, LOW = NO
SW_TEST     = 11    # HIGH = YES, LOW = NO

GPIO.setup(SW_EXT_RST, GPIO.IN)
GPIO.setup(SW_BOOTLD, GPIO.IN)
GPIO.setup(SW_FIRMWARE, GPIO.IN)
GPIO.setup(SW_TEST, GPIO.IN)

# Short detect control outputs
SHORT_CTRL_5V   = 6
SHORT_CTRL_3V3  = 7

GPIO.setup(SHORT_CTRL_5V, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SHORT_CTRL_3V3, GPIO.OUT, initial=GPIO.LOW)

# Shift register outputs
SR_SER  = 16
SR_CLK  = 17
SR_nCLR = 18
SR_RCLK = 19
SR_nOE  = 20

GPIO.setup(SR_SER, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SR_CLK, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SR_nCLR, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SR_RCLK, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(SR_nOE, GPIO.OUT, initial=GPIO.LOW)

# Reset control of Sea-Picro
SP_nRST = 21

GPIO.setup(SP_nRST, GPIO.OUT, initial=GPIO.HIGH)

# Reset and Run sense pins
SP_RUN  = 26
SP_BOOT = 27

GPIO.setup(SP_RUN, GPIO.IN)
GPIO.setup(SP_BOOT, GPIO.IN)

# Load switch enable and fault, removed on the first proto board as it does not work :(
LOAD_SW_nFAULT = 22
LOAD_SW_ENABLE = 23
GPIO.setup(LOAD_SW_nFAULT, GPIO.IN)
GPIO.setup(LOAD_SW_ENABLE, GPIO.IN) # Set to high Z as not in use
# GPIO.setup(LOAD_SW_ENABLE, GPIO.OUT, initial=GPIO.LOW)

def io_set(pin):
    GPIO.output(pin, GPIO.HIGH)

def io_clear(pin):
    GPIO.output(pin, GPIO.LOW)

def led_set(pin):
    GPIO.output(pin, GPIO.LOW)

def led_clear(pin):
    GPIO.output(pin, GPIO.HIGH)

# Sets the IO per bit matrix passed in
def shift_out(bit_matrix, total_pins=23):
    io_set(SR_nCLR)
    io_clear(SR_nOE)
    io_clear(SR_RCLK)

    for i in range(0, total_pins):
        io_clear(SR_CLK)

        if bit_matrix & (1 << i):
            io_clear(SR_SER)
        else:
            io_set(SR_SER)
        io_set(SR_CLK)
        io_clear(SR_SER)

    io_clear(SR_CLK)
    io_set(SR_RCLK)

IO_TO_SR_MAP = [15, 16, 17, 18, 19, 20, 21, 22, 7, 8, 14, 0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13]

adc_init()
while True:
    print("CC: {}".format(adc_read("CC")))
    time.sleep(1)
    print("3V3: {}".format(adc_read("3V3")))
    time.sleep(1)
    print("5V0: {}".format(adc_read("5V0")))
    time.sleep(1)
    