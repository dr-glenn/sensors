# BME280 temp/humid/pressure sensor

import board
import digitalio
import busio
import time
import adafruit_bme280

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
    values['temp_c'] = (device.temperature, 'C', '0.1f')
    values['rel_hum'] = (device.relative_humidity, '%', '0.1f')
    values['pressure'] = (device.pressure, 'hPa', '0.1f')
    values['altitude'] = (device.altitude, 'meters', '0.2f')
    return name,values

def printit(name, values):
    print('Device: {}'.format(name))
    for val_key in values:
        value = values[val_key]
        #val_format = '{} = { %s} {}' %(value[2])    # embed the number format into output format string
        print('{0} = {1:{3}} {2}'.format(val_key, value[0], value[1], value[2]))
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
