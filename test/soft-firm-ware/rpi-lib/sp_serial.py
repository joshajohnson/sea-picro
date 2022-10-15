import serial
from serial.tools import list_ports
import io
from colorama import Fore
import time

global dut_serial_io

def serial_init():
    test_fail = True
    com_port = None
    attempt_counter = 0
    while com_port == None:
        ports = list_ports.comports()
        print(f"{Fore.BLUE}Searching for CircuitPython CDC2 control")
        for p in ports:
            if p.interface == "CircuitPython CDC2 control":
                com_port = p.device
                print(f"{Fore.BLUE}CircuitPython CDC2 control found on " + com_port)
                break

        time.sleep(1)
        attempt_counter = attempt_counter + 1
        if attempt_counter > 10:
            print(f'{Fore.RED}TIMEOUT TRYING TO FIND Circuitpython CDC2!')
            break
    
    if com_port != None:
        attempt_counter = 0
        while attempt_counter < 10:
            try:
                time.sleep(1)
                global dut_serial_io
                data = serial.Serial(com_port, 115200, timeout=0.1)
                dut_serial_io = io.TextIOWrapper(io.BufferedRWPair(data, data))
                print(f"{Fore.BLUE}Serial port opened")
                test_fail = False
                break
            except:
                print(f'{Fore.BLUE}Unable to connect to DUT serial port, retrying.')
                test_fail = True
                attempt_counter = attempt_counter + 1


        if test_fail:
            print(f'{Fore.BLUE}Timeout whilst connecting to DUT serial port.')
        
    return test_fail

def send_dut_string(string):
    retry = 0
    while retry < 3:
        try:
            dut_serial_io.write(str(string) + "\r\n")
            dut_serial_io.flush()
            break
        except:
            print(f'{Fore.RED}Issue sending DUT string')
            retry = retry + 1
            time.sleep(1)

def get_dut_string():
    retry = 0
    while retry < 3:
        try:
            return dut_serial_io.readline()[0:-1]
        except:
            print(f'{Fore.RED}Issue getting DUT string')
            retry = retry + 1
            time.sleep(1)