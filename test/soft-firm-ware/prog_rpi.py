import RPi.GPIO as GPIO
from time import sleep

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

GPIO.setup(SR_SER, GPIO.OUT, initial=GPIO.HIGH)

# Reset and Run sense pins
SP_RUN  = 26
SP_BOOT = 27

GPIO.setup(SP_RUN, GPIO.IN)
GPIO.setup(SP_BOOT, GPIO.IN)

# Load switch enable and fault
LOAD_SW_nFAULT = 22
LOAD_SW_ENABLE = 23

GPIO.setup(LOAD_SW_nFAULT, GPIO.IN)
GPIO.setup(LOAD_SW_ENABLE, GPIO.OUT, initial=GPIO.LOW)

while True:
    # GPIO.output(LED_RED, GPIO.HIGH)
    # GPIO.output(LED_GREEN, GPIO.LOW)
    # sleep(1)
    # GPIO.output(LED_RED, GPIO.LOW)
    # GPIO.output(LED_GREEN, GPIO.HIGH)
    # sleep(1)

    if GPIO.input(SW_TEST) == GPIO.HIGH:
        GPIO.output(LED_RED, GPIO.HIGH)
    else:
        GPIO.output(LED_RED, GPIO.LOW)