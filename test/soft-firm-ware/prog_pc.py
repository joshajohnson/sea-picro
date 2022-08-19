#!/bin/python3

# Script to program and test sea-picro

import os
import time
import argparse
from colorama import Fore
import serial
from serial.tools import list_ports
import usb.core
import io
from multiprocessing import Process

bl_vid = 0x2e8a
bl_pid = 0x0003

cpy_vid = 0x6a6a
cpy_pid = 0x5350

# Order is RST pins anticlockwise, then EXT pins anticlockwise
sp_pin_map = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D21", "D23", "D20", "D22", "D26", "D27", "D28", "D29", "D12", "D13", "D14", "D15", "D16"]

def flash_circuitpython():
    ''' Flashes circuitpython firmware. '''
    test_fail = False
    found_rpi = False
    # Spinlock until RPi bootloader is found
    while found_rpi == False:
        dev = usb.core.find(find_all=1)
        for cfg in dev:
            if cfg.idVendor == bl_vid and cfg.idProduct == bl_pid:
                found_rpi = True
        time.sleep(1)

    time.sleep(2)
    print("RPi Bootloader found, copying CircuitPython")
    retval = os.system("cp circuitpy-sea-picro.uf2 /media/josh/RPI-RP2")
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
            if cfg.idVendor == cpy_vid and cfg.idProduct == cpy_pid:
                found_cpy = True
        time.sleep(1)

    print("CircuitPython found, copying test firmware")
    time.sleep(5)
    retval = os.system("cp -rf circuitpy-files/* /media/josh/CIRCUITPY")
    if retval != 0:
        print(f'{Fore.RED}FAILED TO FLASH TEST FW !')
        test_fail = True

    return test_fail


def send_tester_string(string):
    tester_serial_io.write(str(string) + "\r\n")
    tester_serial_io.flush()

def get_tester_string():
    ret_str = tester_serial_io.readline()
    return ret_str

def send_dut_string(string):
    dut_serial_io.write(str(string) + "\r\n")
    dut_serial_io.flush()

def get_dut_string():
    ret_str = dut_serial_io.readline()[0:-1]
    return ret_str

def test_ident():
    # Check we have the right /dev/ttyACM port
    test_fail = False
    send_dut_string("ident")
    ret_str = get_dut_string()

    if ret_str == "ident = Sea-Picro!":
        print(f'{Fore.BLUE}IDENT passed')
    else:
        send_tester_string(33) # Error
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
        send_tester_string(33) # Error
        print(f'{Fore.RED}VBUS detect failed')
    else:
        send_tester_string(33) # Error
        print(f'{Fore.RED}VBUS detect failed')
        test_fail = True

    return test_fail

def test_led():
    # RGB test time
    test_fail = False
    print(f'{Fore.YELLOW}Monitor LEDs please')
    send_dut_string("led_red")
    time.sleep(2)
    send_dut_string("led_grn")
    time.sleep(1)
    send_dut_string("led_blu")
    time.sleep(1)
    
    print(f'{Fore.YELLOW}Did LEDs cycle R/G/B? (Y)es / (N)o / (R)epeat{Fore.WHITE}')

    recv = input()

    if recv.lower() == "y":
        print(f'{Fore.BLUE}RGB LEDs passed')
        send_dut_string("led_rgb") # Party Time!
    elif recv.lower() == "n":
        send_tester_string(33) # Error
        print(f'{Fore.RED}RGB LEDs failed')
        test_fail = True
    elif recv.lower() == "r":
        test_led()

    return test_fail

def test_keys(model):
    ''' Test all IO with test fixture.
    Transmit number according to pin location, which test fixture will pull low, simulating key press.
    DUT will then respond with a bitfield showing IO state. '''
    test_fail = False

    if model == "rst":
        num_io = 18 # RST has 18 IO
    if model == "ext":
        num_io == 23 # EXT has 23 IO

    for pos in range(1,num_io+1):
        send_tester_string(pos)
        time.sleep(0.1)
        send_dut_string("io_test")
        ret_str = get_dut_string()

        array = ret_str[1:-1].split(", ") # Convert to array of strings "True", "False"

        key_fail = False # Used to flag if a key passes it's test or not

        # Loop through array and check val = False unless index == pos
        for index in range(0,num_io):
            # Case where we expect a key to be pressed
            if index == pos-1:
                if array[index] == "True":
                    pass
                else:
                    send_tester_string(33) # Error
                    print(f'{Fore.RED}{sp_pin_map[pos-1]}: IO {sp_pin_map[index]} was NOT pressed')
                    key_fail = key_fail or True
                    test_fail = True

            # Case where we do not expect a key to be pressed
            elif index != pos-1:
                if array[index] == "False":
                    pass
                else:
                    send_tester_string(33) # Error
                    print(f'{Fore.RED}{sp_pin_map[pos-1]}: IO {sp_pin_map[index]} WAS pressed')
                    key_fail = key_fail or True
                    test_fail = True

        if not key_fail:
            print(f'{Fore.BLUE}{sp_pin_map[pos-1]}: IO {sp_pin_map[pos-1]} passed') # Print passed message if a fail message hasn't been printed


    return test_fail

def test_dut(model):

    test_fail = False

    test_fail = test_fail or test_ident()
    test_fail = test_fail or test_vbus()
    test_fail = test_fail or test_led()
    test_fail = test_fail or test_keys(model)

    return test_fail

if __name__ == "__main__":

    # Connect to test fixture
    tester_serial_io = None
    # ACM0 = arduino
    # ACM1 = cpy repl
    # ACM2 = cpy data
    try:
        uart = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
        tester_serial_io = io.TextIOWrapper(io.BufferedRWPair(uart, uart))
    except:
        print(f'{Fore.RED}Conneting to tester failed, possibly wrong /dev/ttyACM port')
        exit()

    try:
        data = serial.Serial("/dev/ttyACM2", 115200, timeout=0.1)
        dut_serial_io = io.TextIOWrapper(io.BufferedRWPair(data, data))
    except:
        print(f'{Fore.RED}Conneting to DUT failed, possibly wrong /dev/ttyACM port')
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--circuitpython",action='store_true')
    parser.add_argument("-f", "--firmware",     action='store_true')
    parser.add_argument("-r", "--rst_test",     action='store_true')
    parser.add_argument("-e", "--ext_test",     action='store_true')
    args = parser.parse_args()

    send_tester_string(34) # Reset status LEDs
    test_fail = False

    if args.circuitpython:
        test_fail = test_fail | flash_circuitpython()
    if args.firmware:
        test_fail = test_fail | flash_firmware()
        time.sleep(5)
    if args.rst_test:
        test_fail = test_fail | test_dut("rst")

    if test_fail == False:
        send_tester_string(32) # Status OKAY
        print(f'{Fore.GREEN}ALL STEPS PASSED!!!')
    elif test_fail == True:
        send_tester_string(33) # Status FAIL
        print(f'{Fore.RED}TEST FAILED!!!')

