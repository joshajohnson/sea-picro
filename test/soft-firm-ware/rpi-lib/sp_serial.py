import serial
import io
from colorama import Fore

global dut_serial_io

def serial_init():
    # try:
    global dut_serial_io
    data = serial.Serial("/dev/ttyACM1", 115200, timeout=0.1) # ACM1 is the debug port, ACM0 is the REPL
    dut_serial_io = io.TextIOWrapper(io.BufferedRWPair(data, data))
    # except:
        # print(f'{Fore.RED}Unable to connect to DUT serial port, check connections.')
        # exit()

def send_dut_string(string):
    dut_serial_io.write(str(string) + "\r\n")
    dut_serial_io.flush()

def get_dut_string():
    return dut_serial_io.readline()[0:-1]