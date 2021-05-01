# -*- coding: utf-8 -*-
# BME280 temp/humid/pressure sensor

import board
#import digitalio
import busio
import time
import adafruit_bme280
from .device import Device

class BME280(Device):
    dev_name = 'bme280'
    sensor_def = {}   # define various sensors
    sensor_def['temp_c'] = ('temperature', u'\N{DEGREE SIGN}C', '0.1f')
    sensor_def['rel_hum'] = ('relative humidity', '%', '0.1f')
    sensor_def['pressure'] = ('pressure', ' hPa', '0.1f')
    sensor_def['altitude'] = ('altitude', ' meters', '0.1f')
    def __init__(self, sys_name):
        super().__init__(sys_name)
        name, self.device = get_device(sys_name)

    @classmethod
    def get_sensor_keys(cls):
        return list(cls.sensor_def.keys())

    def get_values(self):
        name, self.values = get_values(self.sys_name, self.device)
        return self.values

    @classmethod
    def get_str_value(cls, key, value):
        '''
        Format sensor value according to sensor_def.
        :param key: name of value, e.g., temp_c
        :param value: numeric value from the sensor
        :return: example: '15.0 C' for temperature
        '''
        strValue = '{0:{1}}{2}'.format(value, cls.sensor_def[key][2], cls.sensor_def[key][1])
        return strValue

    @classmethod
    def printall(cls, values):
        # iterate over all values returned from device
        for v in values:
            sens_form = cls.sensor_def[v]
            print('{}: {}'.format(sens_form[0], cls.get_str_value(v,values[v])))

def get_device(name='pi'):
    '''
    Get a BME280 device handle.
    :param name: unique identifier for this BME device
    :return: device handle
    TODO: figure out how to access multiple sensors
    '''
    # Create library object using our Bus I2C port
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
    #or with other sensor address
    #bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

    # OR create library object using our Bus SPI port
    #spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
    #bme_cs = digitalio.DigitalInOut(board.D10)
    #bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, bme_cs)

    # change this to match the location's pressure (hPa) at sea level
    bme280.sea_level_pressure = 1013.25
    return name,bme280

def get_values(name='pi',device=None):
    '''
    Read all sensors and return as dict.
    :return: dict of values
    '''
    if not device:
        name,device = get_device()
    values = {}
    values['temp_c'] = device.temperature
    values['rel_hum'] = device.relative_humidity
    values['pressure'] = device.pressure
    values['altitude'] = device.altitude
    return name,values

def printit(name, values):
    print('Device: {}'.format(name))
    for val_key in values:
        value = values[val_key]
        #val_format = '{} = { %s} {}' %(value[2])    # embed the number format into output format string
        print('{0} = {1}'.format(val_key, value))
    """
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.relative_humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    print("Altitude = %0.2f meters" % bme280.altitude)
    """

if __name__ == '__main__':
    name,bme280 = get_values()
    while True:
        printit(name,bme280)
        time.sleep(2)
