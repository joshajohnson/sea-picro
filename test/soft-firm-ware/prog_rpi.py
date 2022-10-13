# System imports
import RPi.GPIO as GPIO
import time
import sys
import os
from colorama import Fore
import serial
from serial.tools import list_ports
import usb.core

# Local imports
sys.path.append("rpi-lib")
from sp_io import *
from adc import *
from shift_reg import *
from sp_serial import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

RST  = 17
EXT  = 23
dut_type = None
# Map between IO position on Sea-Picro and location in shift reg chain
IO_TO_SR_MAP = [15, 16, 17, 18, 19, 20, 21, 22, 7, 8, 14, 0, 1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13]
# IO list of SP in same order as above
SP_PIN_MAP = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D21", "D23", "D20", "D22", "D26", "D27", "D28", "D29", "D12", "D13", "D14", "D15", "D16"]

# USB strings
RPI_VID = 0x2e8a
RPI_PID = 0x0003

CPY_VID = 0x6a6a
CPY_PID = 0x5350

def flash_circuitpython():
    ''' Flashes circuitpython firmware. '''
    test_fail = False

    found_rpi = False
    # Spinlock until RPi bootloader is found
    while found_rpi == False:
        dev = usb.core.find(find_all=1)
        for cfg in dev:
            if cfg.idVendor == RPI_VID and cfg.idProduct == RPI_PID:
                found_rpi = True
        print(f"{Fore.BLUE}Searching for Bootloader")
        time.sleep(1)

    time.sleep(3)
    print(f"{Fore.BLUE}RPi Bootloader found, copying CircuitPython")
    retval = os.system("cp circuitpy-sea-picro.uf2 /media/pi/RPI-RP2")
    if retval != 0:
        print(f'{Fore.RED}FAILED TO FLASH CPY !')
        test_fail = True

    return test_fail

def flash_firmware():
    ''' Flashes test firmware. '''
    test_fail = False
    found_cpy = False
    # Spinlock until circuitpython is found
    while found_cpy == False:
        dev = usb.core.find(find_all=1)
        for cfg in dev:
            if cfg.idVendor == CPY_VID and cfg.idProduct == CPY_PID:
                found_cpy = True
        time.sleep(1)

    print(f"{Fore.BLUE}CircuitPython found, copying test firmware")
    time.sleep(5)
    retval = os.system("cp -rf circuitpy-files/* /media/pi/CIRCUITPY")
    if retval != 0:
        print(f'{Fore.RED}FAILED TO FLASH TEST FW !')
        test_fail = True
    else:
        sp_reset()

    return test_fail

def test_ident():
    # Check we have the right /dev/ttyACM port
    test_fail = False
    send_dut_string("ident")
    ret_str = get_dut_string()

    if ret_str == "ident = Sea-Picro!":
        print(f'{Fore.BLUE}IDENT passed')
    else:
        led_fail()
        print(f'{Fore.RED}IDENT Failed, possibly wrong /dev/ttyACM port')
        test_fail = True

    return test_fail

def test_vbus():
    # Check VBUS detection
    test_fail = False
    send_dut_string("vbus_test")
    ret_str = get_dut_string()

    if ret_str == "vbus = high":
        print(f'{Fore.BLUE}VBUS detect passed')
    elif ret_str == "vbus = low":
        led_fail()
        print(f'{Fore.RED}VBUS detect failed')
    else:
        led_fail()
        print(f'{Fore.RED}VBUS detect failed')
        test_fail = True

    return test_fail

def test_led():
    # RGB test time
    test_fail = False
    print(f'{Fore.YELLOW}Monitor LEDs please')
    send_dut_string("led_rgb")
    
    print(f'{Fore.YELLOW}Did LEDs cycle R/G/B? (Y)es / (N)o / (R)epeat{Fore.WHITE}')
    time.sleep(3)
    recv = input()

    if recv.lower() == "y":
        print(f'{Fore.BLUE}RGB LEDs passed')
        send_dut_string("led_rbw") # Party Time!
    elif recv.lower() == "n":
        led_fail()
        print(f'{Fore.RED}RGB LEDs failed')
        test_fail = True
    elif recv.lower() == "r":
        test_led()

    time.sleep(2)

    return test_fail

def test_cc():
    cc_val = adc_read("CC")

    if cc_val < 3000:
        print(f'{Fore.BLUE}CC pin passed')
        return True
    else:
        print(f'{Fore.RED}CC pin failed')
        return False

def test_io():
    pass # TODO

def test_dut(model):

    test_fail = False

    test_fail = test_fail or test_ident()
    test_fail = test_fail or test_vbus()
    test_fail = test_fail or test_cc()
    test_fail = test_fail or test_led()
    # test_fail = test_fail or test_io(model)

# Init all the things!
io_init()
adc_init()
shift_reg_init()
while True:
    print(f"{Fore.YELLOW}Press YES to begin test!")
    led_reset()
    while True:
        if (io_get(SW_YES)):
            time.sleep(0.1) # Shitty debounce
            print(f"{Fore.BLUE}Beginning test!")
            test_fail = False

            # Configure tester for EXT or RST
            if (io_get(SW_EXT_RST)):
                print(f"{Fore.BLUE}DUT = EXT")
                dut_type = EXT
            else:
                print(f"{Fore.BLUE}DUT = RST")
                dut_type = RST

            # Check if we need to flash cpy or not
            if (io_get(SW_BOOTLD)):
                # Need to reset board to throw into bootloader
                sp_bootloader()
                flash_circuitpython()

            # Check if we need to flash firmare / test code
            if (io_get(SW_FIRMWARE)):
                flash_firmware()

            if (io_get(SW_TEST)):
                time.sleep(10)
                print (list_ports.main())
                serial_init()
                test_dut(dut_type)

            if test_fail == False:
                print(f'{Fore.GREEN}ALL STEPS PASSED!!!')
            elif test_fail == True:
                print(f'{Fore.RED}TEST FAILED!!!')

            break

