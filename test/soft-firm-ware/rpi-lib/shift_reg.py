import RPi.GPIO as GPIO
import sys

sys.path.append("rpi-lib")
from sp_io import *

SR_SER  = 16
SR_CLK  = 17
SR_nCLR = 18
SR_RCLK = 19
SR_nOE  = 20

def shift_reg_init():
    GPIO.setup(SR_SER, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SR_CLK, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SR_nCLR, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SR_RCLK, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(SR_nOE, GPIO.OUT, initial=GPIO.LOW)

def shift_out(bit_matrix):
    io_high(SR_nCLR)
    io_low(SR_nOE)
    io_low(SR_RCLK)

    for i in range(0, 23):  # There are 23 pins connected to the shift register
        io_low(SR_CLK)

        if bit_matrix & (1 << i):
            io_low(SR_SER)
        else:
            io_high(SR_SER)
        io_high(SR_CLK)
        io_low(SR_SER)

    io_low(SR_CLK)
    io_high(SR_RCLK)