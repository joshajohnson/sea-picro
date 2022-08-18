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

def flash_circuitpython():
    ''' Flashes circuitpython firmware. '''
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
        print(f'{Fore.RED}#####################')
        print(f'{Fore.RED}FAILED TO FLASH CPY !')
        print(f'{Fore.RED}#####################')
        exit()

def flash_firmware():
    ''' Flashes test firmware. '''
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
        print(f'{Fore.RED}#########################')
        print(f'{Fore.RED}FAILED TO FLASH TEST FW !')
        print(f'{Fore.RED}#########################')
        exit()


def send_string(string):
    serial_io.write(str(string) + "\r\n")
    serial_io.flush()

def test_keys():
    ''' Test all IO with test fixture.
        Transmit number according to pin location, which test fixture will pull low, simulating key press.
        DUT will then respond with the alpha character (A=1, B=2 etc) which we can check. '''

    for char in range(1,19): # sea-picro has 18 IO

        alpha = chr(96 + char)

        # Transmit required char, and compare to what we want
        send_string(char)

        recv = input()
        print(f'Requested: {alpha} Received: {str(recv)}')

        if recv != alpha: # retry once

            print("Trying Again!")
            send_string(char)

            recv = input()
            print(f'Requested: {alpha} Received: {str(recv)}') 

            if recv != alpha:
                send_string(33) # Error
                print(f'{Fore.RED}###############')
                print(f'{Fore.RED}NOT TYPING {alpha} !!!')
                print(f'{Fore.RED}###############')
                exit()

    print(f'{Fore.BLUE}KEYS TEST PASSED{Fore.WHITE}')

if __name__ == "__main__":

    # Connect to test fixture
    serial_io = None
    uart = serial.Serial("/dev/ttyACM0", 115200, timeout=0.1)
    serial_io = io.TextIOWrapper(io.BufferedRWPair(uart, uart))

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--circuitpython",action='store_true')
    parser.add_argument("-f", "--firmware",     action='store_true')
    parser.add_argument("-t", "--test",         action='store_true')
    args = parser.parse_args()

    send_string(34) # Reset status LEDs

    if args.circuitpython:
        flash_circuitpython()
    if args.firmware:
        flash_firmware()
        time.sleep(5)
    if args.test:
        test_keys()        

    send_string(32) # Status OKAY
    print(f'{Fore.GREEN}###################')
    print(f'{Fore.GREEN}ALL STEPS PASSED!!!')
    print(f'{Fore.GREEN}###################{Fore.WHITE}')
