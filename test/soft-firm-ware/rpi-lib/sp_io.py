import RPi.GPIO as GPIO
import time

# Active low output
LED_RED     = 12
LED_GREEN   = 13

# Active high input
SW_YES  = 4
SW_NO   = 5

# Input
SW_EXT_RST  = 8     # HIGH = EXT, LOW = RST
SW_BOOTLD   = 9     # HIGH = YES, LOW = NO
SW_FIRMWARE = 10    # HIGH = YES, LOW = NO
SW_TEST     = 11    # HIGH = YES, LOW = NO

# Outputs
SHORT_CTRL_5V   = 6
SHORT_CTRL_3V3  = 7

# Active low output
SP_nRST = 21

# Input sense pins
SP_RUN  = 26
SP_BOOT = 27

# Active low input / active high output
LOAD_SW_nFAULT = 22
LOAD_SW_ENABLE = 23

def io_init():
    # Output LEDs, active low
    GPIO.setup(LED_RED, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.HIGH)

    # Push buttons for user input, active high
    GPIO.setup(SW_YES, GPIO.IN)
    GPIO.setup(SW_NO, GPIO.IN)

    # Slide switches for mode select
    GPIO.setup(SW_EXT_RST, GPIO.IN)
    GPIO.setup(SW_BOOTLD, GPIO.IN)
    GPIO.setup(SW_FIRMWARE, GPIO.IN)
    GPIO.setup(SW_TEST, GPIO.IN)

    # Short detect control outputs
    GPIO.setup(SHORT_CTRL_5V, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(SHORT_CTRL_3V3, GPIO.OUT, initial=GPIO.LOW)

    # Reset control of Sea-Picro
    GPIO.setup(SP_nRST, GPIO.OUT, initial=GPIO.HIGH)

    # Reset and Run sense pins
    GPIO.setup(SP_RUN, GPIO.IN)
    GPIO.setup(SP_BOOT, GPIO.IN)

    # Load switch enable and fault, removed on the first proto board as it does not work :(
    GPIO.setup(LOAD_SW_nFAULT, GPIO.IN)
    GPIO.setup(LOAD_SW_ENABLE, GPIO.IN) # Set to high Z as not in use
    # GPIO.setup(LOAD_SW_ENABLE, GPIO.OUT, initial=GPIO.LOW)

def io_set(pin):
    GPIO.output(pin, GPIO.HIGH)

def io_clear(pin):
    GPIO.output(pin, GPIO.LOW)

def io_get(pin):
    return not GPIO.input(pin)

def led_set(pin):
    GPIO.output(pin, GPIO.LOW)

def led_clear(pin):
    GPIO.output(pin, GPIO.HIGH)

def led_reset():
    led_clear(LED_GREEN)
    led_clear(LED_RED)

def led_fail():
    led_set(LED_RED)
    led_clear(LED_GREEN)

def led_pass():
    led_set(LED_GREEN)
    led_clear(LED_RED)

def sp_reset():
    io_clear(SP_nRST)
    time.sleep(0.1)
    io_set(SP_nRST)

def sp_bootloader():
    io_clear(SP_nRST)
    time.sleep(1)
    io_set(SP_nRST)