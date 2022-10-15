import RPi.GPIO as GPIO
import time
from colorama import Fore

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

def io_high(pin):
    GPIO.output(pin, GPIO.HIGH)

def io_low(pin):
    GPIO.output(pin, GPIO.LOW)

def io_read(pin):
    return GPIO.input(pin)

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
    io_low(SP_nRST)
    time.sleep(0.3)
    io_high(SP_nRST)

def sp_bootloader():
    test_fail = False
    # Hold reset low for a second
    io_low(SP_nRST)
    time.sleep(1.5)
    if (io_read(SP_RUN) == False) and (io_read(SP_BOOT) == False):
        pass
    else:
        print(f'{Fore.RED}RESET HOLD LOW FAIL: RUN: {io_read(SP_RUN)} BOOT: {io_read(SP_BOOT)} (Expected R:0 B:0)')
        test_fail = test_fail | True

    # Release reset button
    io_high(SP_nRST)
    time.sleep(0.02)
    if (io_read(SP_RUN) == True) and (io_read(SP_BOOT) == False):
        pass
    else:
        print(f'{Fore.RED}BOOT ENTRY CONDITION FAIL: RUN: {io_read(SP_RUN)} BOOT: {io_read(SP_BOOT)} (Expected R:1 B:0)')
        test_fail = test_fail | True

    time.sleep(0.2)
    if (io_read(SP_RUN) == True) and (io_read(SP_BOOT) == True):
        pass
    else:
        print(f'{Fore.RED}NORMAL OPERATION FAIL: RUN: {io_read(SP_RUN)} BOOT: {io_read(SP_BOOT)} (Expected R:1 B:1)')
        test_fail = test_fail | True

    if test_fail == False:
        print(f"{Fore.BLUE}One button reset circuit working correctly")

    return test_fail