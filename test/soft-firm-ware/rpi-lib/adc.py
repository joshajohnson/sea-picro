import smbus
import time

global bus

def adc_init():
    # Get I2C bus
    global bus 
    bus = smbus.SMBus(1)
    # Init to automatic conversion mode (Register 0x02, value 0x20 (32 dec))
    bus.write_byte_data(0x50, 0x02, 0x20)
    bus.write_byte_data(0x51, 0x02, 0x20)
    bus.write_byte_data(0x52, 0x02, 0x20)

def adc_read(adc):
    if adc == "CC":
        adc_count = bus.read_i2c_block_data(0x51, 0x00, 2)
    elif adc == "3V3":
        adc_count = bus.read_i2c_block_data(0x50, 0x00, 2)
    elif adc == "5V0":
        adc_count = bus.read_i2c_block_data(0x52, 0x00, 2)
    
    # Convert the data to 12-bits
    raw_adc = (adc_count[0] & 0x0F) * 256 + adc_count[1]
    # Convert to mV
    mv = int(raw_adc / 2 **12 * 5200)

    return mv