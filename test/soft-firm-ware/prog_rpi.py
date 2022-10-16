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
from oled import *

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

global fail_str
fail_str = ""

def flash_circuitpython():
    ''' Flashes circuitpython firmware. '''
    global fail_str
    test_fail = True
    found_rpi = False
    attempt_counter = 0
    # Spinlock until RPi bootloader is found
    while found_rpi == False:
        print(f"{Fore.BLUE}Searching for RP2040 bootloader")
        dev = usb.core.find(find_all=1)
        for cfg in dev:
            if cfg.idVendor == RPI_VID and cfg.idProduct == RPI_PID:
                found_rpi = True
        time.sleep(1)
        attempt_counter = attempt_counter + 1
        if attempt_counter > 5:
            print(f'{Fore.RED}TIMEOUT TRYING TO FIND BOOTLOADER!')
            fail_str = "CPY"
            test_fail = True
            break

    if found_rpi:
        print(f"{Fore.BLUE}Bootloader found, copying CircuitPython")
        oled_write("Flashing CPY")
        time.sleep(3)
        retval = os.system("cp circuitpy-sea-picro.uf2 /media/pi/RPI-RP2")
        if retval != 0:
            print(f'{Fore.RED}FAILED TO FLASH CIRCUITPYTHON!')
            fail_str = "CPY"
            test_fail = True
        else:
            test_fail = False

    return test_fail

def flash_firmware():
    ''' Flashes test firmware. '''
    global fail_str
    test_fail = True
    found_cpy = False
    attempt_counter = 0
    # Spinlock until circuitpython is found
    while found_cpy == False:
        print(f"{Fore.BLUE}Searching for Circuitpython")
        dev = usb.core.find(find_all=1)
        for cfg in dev:
            if cfg.idVendor == CPY_VID and cfg.idProduct == CPY_PID:
                found_cpy = True
        time.sleep(1)
        
        attempt_counter = attempt_counter + 1
        if attempt_counter > 15:
            print(f'{Fore.RED}TIMEOUT TRYING TO FIND CIRCUITPYTHON!')
            fail_str = "FW"
            test_fail = True
            break

    if found_cpy:
        print(f"{Fore.BLUE}CircuitPython found, copying test firmware")
        oled_write("Flashing Test FW")
        time.sleep(5)
        retval = os.system("cp -rf circuitpy-files/* /media/pi/CIRCUITPY")
        if retval != 0:
            print(f'{Fore.RED}FAILED TO FLASH TEST FIRMWARE!')
            fail_str = "FW"
            test_fail = True
        else:
            test_fail = False
            sp_reset()
            time.sleep(3)

    return test_fail

def test_ident():
    # Check we have the right /dev/ttyACM port
    global fail_str
    test_fail = True
    send_dut_string("ident")
    ret_str = get_dut_string()

    if ret_str == "ident = Sea-Picro!":
        print(f'{Fore.BLUE}IDENT passed')
        test_fail = False
    else:
        print(f'{Fore.RED}IDENT Failed, possibly wrong /dev/ttyACM port')
        fail_str = "IDENT"
        test_fail = True

    return test_fail

def test_vbus():
    # Check VBUS detection
    global fail_str
    test_fail = True
    send_dut_string("vbus_test")
    ret_str = get_dut_string()

    if ret_str == "vbus = high":
        print(f'{Fore.BLUE}VBUS detect passed')
        test_fail = False
    else:
        print(f'{Fore.RED}VBUS detect failed')
        fail_str = "VBUS"

    return test_fail

def test_led():
    # RGB test time
    global fail_str
    test_fail = True
    print(f'{Fore.YELLOW}Monitor LEDs please')
    send_dut_string("led_rgb")
    
    print(f'{Fore.YELLOW}Did LEDs cycle R/G/B? YES / NO {Fore.WHITE}')
    oled_write("LEDs R/G/B?")
    time.sleep(1) # delay long enough that the operator has seen all colours work

    while True:
        if (not io_read(SW_YES)):
            print(f'{Fore.BLUE}RGB LEDs passed')
            test_fail = False
            send_dut_string("led_off")
            time.sleep(0.1)
            break
        if (not io_read(SW_NO)):
            print(f'{Fore.RED}RGB LEDs failed')
            send_dut_string("led_off")
            time.sleep(0.1)
            fail_str = "RGB"
            break

    return test_fail

def test_cc():
    global fail_str
    cc_val = adc_read("CC")

    if cc_val < 3000:
        print(f'{Fore.BLUE}CC pin passed')
        return False
    else:
        print(f'{Fore.RED}CC pin failed')
        fail_str = "CC"
        return True

def test_io(model):
    global fail_str
    test_fail = False
    for pos in range(0, model):
        shift_out((1 << IO_TO_SR_MAP[pos]))
        send_dut_string("io_test")
        ret_str = get_dut_string()

        array = ret_str[1:-1].split(", ") # Convert to array of strings "True", "False"

        key_fail = False # Used to flag if a key passes it's test or not

        # Loop through array and check val = False unless index == pos
        for index in range(0,model):
            # Case where we expect a key to be pressed
            if index == pos:
                if array[index] == "True":
                    pass
                else:
                    print(f'{Fore.RED}{SP_PIN_MAP[pos]}: IO {SP_PIN_MAP[index]} was NOT pressed')
                    key_fail = True
                    test_fail = True

            # Case where we do not expect a key to be pressed
            elif index != pos:
                if array[index] == "False":
                    pass
                else:
                    print(f'{Fore.RED}{SP_PIN_MAP[pos]}: IO {SP_PIN_MAP[index]} WAS pressed')
                    key_fail = True
                    test_fail = True

        if not key_fail:
            print(f'{Fore.BLUE}{SP_PIN_MAP[pos]}: IO {SP_PIN_MAP[pos]} passed')

        if test_fail:
            fail_str = "IO"

    return test_fail

def test_dut(model):

    test_fail = False
    oled_write("Testing DUT")
    # Don't continue testing if we can't ident properly
    if test_ident():
        return True

    test_fail = test_fail | test_vbus()
    test_fail = test_fail | test_cc()
    test_fail = test_fail | test_io(model)
    test_fail = test_fail | test_led()

    return test_fail 

# Init all the things!
io_init()
adc_init()
shift_reg_init()
oled_init()

time.sleep(1)
retest = False
test_only = False
# Super loop time
while True:
    if not retest:
        print(f"{Fore.YELLOW}Press YES to begin test!")
        oled_write("Begin Test?", size=20)
    retest = False
    while True:
        # try:
            if (not io_read(SW_YES) or test_only):
                time.sleep(0.1) # Shitty debounce
                led_reset()
                print(f"{Fore.BLUE}Beginning test!")
                test_fail = False

                # Configure tester for EXT or RST
                if (not io_read(SW_EXT_RST)):
                    print(f"{Fore.BLUE}Sea-Picro EXT selected")
                    oled_write("Testing EXT")
                    dut_type = EXT
                else:
                    print(f"{Fore.BLUE}Sea-Picro RST selected")
                    oled_write("Testing RST")
                    dut_type = RST

                # Check if we need to flash cpy or not
                if (not io_read(SW_BOOTLD) and (test_fail == False) and not test_only):
                    # Need to reset board to throw into bootloader
                    # We also check the reset circuit is working correctly here
                    test_fail = sp_bootloader()
                    if test_fail == True:
                        fail_str = "RESET"
                    else:
                        test_fail = flash_circuitpython()

                # Check if we need to flash firmare / test code
                if (not io_read(SW_FIRMWARE) and (test_fail == False) and not test_only):
                    test_fail = flash_firmware()

                # Check if we need to test the DUT
                if (not io_read(SW_TEST) and (test_fail == False)):
                    sp_reset() # Need to power cut here
                    test_fail = serial_init()
                    if test_fail == True:
                        fail_str = "CDC2"
                        # Need to power cut here
                    else:
                        test_fail = test_dut(dut_type)
                    
                    # If we are just doing the final test, check the reset circuit
                    if (io_read(SW_BOOTLD) and io_read(SW_FIRMWARE) and (test_fail == False)) or (test_only and test_fail == False):
                        test_fail = sp_bootloader()
                        if test_fail == True:
                            fail_str = "RESET"
                        # Need to power cut here

                test_only = False
                # Advise user on how everything went
                if test_fail == False:
                    print(f'{Fore.GREEN}ALL STEPS PASSED!!!')
                    print(f"{Fore.YELLOW}Press YES for full test, NO for final test")
                    oled_write_dual("Test Passed!", "Y: FULL N: FINAL", size2 = 12)
                    retest = True
                    led_pass()
                    while True:
                        if (not io_read(SW_YES)):
                            break
                        if (not io_read(SW_NO)):
                            test_only = True
                            break
                elif test_fail == True:
                    print(f'{Fore.RED}TEST FAILED: {fail_str}')
                    print(f"{Fore.YELLOW}Press YES for full test, NO for final test")
                    oled_write_dual(f'FAIL: {fail_str}', "Y: FULL N: FINAL", size2 = 12)
                    retest = True
                    led_fail()
                    while True:
                        if (not io_read(SW_YES)):
                            break
                        if (not io_read(SW_NO)):
                            test_only = True
                            break
                break
        # except:
        #     print(f"{Fore.RED}Something went wrong, let's try again")
        #     break

