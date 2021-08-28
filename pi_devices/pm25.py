"""
Example sketch to connect to PM2.5 sensor with either I2C or UART.
"""

# pylint: disable=unused-import
import time
import board
import busio
import RPi.GPIO as GPIO
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
import datetime as dt
from .device import Device

PM25_WAKE_TIME = 30 # PM25 needs to be turned on for this many seconds before ready
PM25_SET_PIN = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(PM25_SET_PIN, GPIO.OUT)
GPIO.output(PM25_SET_PIN, GPIO.HIGH)

class PM25(Device):
    dev_name = 'pm25'
    sensor_def = {}   # define various sensors
    # unit, display format
    sensor_def['pm10 standard'] = ('PM1.0 standard', '', 'd')
    sensor_def['pm25 standard'] = ('PM2.5 standard', '', 'd')
    sensor_def['pm100 standard'] = ('PM10.0 standard', '', 'd')
    sensor_def['pm10 env'] = ('PM1.0 env', '', 'd')
    sensor_def['pm25 env'] = ('PM2.5 env', '', 'd')
    sensor_def['pm100 env'] = ('PM10.0 env', '', 'd')
    sensor_def['particles 03um'] = ('Particles > 0.3um', '', 'd')
    sensor_def['particles 05um'] = ('Particles > 0.5um', '', 'd')
    sensor_def['particles 10um'] = ('Particles > 1.0um', '', 'd')
    sensor_def['particles 25um'] = ('Particles > 2.5um', '', 'd')
    sensor_def['particles 50um'] = ('Particles > 5.0um', '', 'd')
    sensor_def['particles 100um'] = ('Particles > 10 um', '', 'd')

    def __init__(self, sys_name):
        super().__init__(sys_name)
        name, self.device = get_device(sys_name)

    @classmethod
    def wake(cls):
        GPIO.output(PM25_SET_PIN, GPIO.HIGH)

    @classmethod
    def sleep(cls):
        GPIO.output(PM25_SET_PIN, GPIO.LOW)

    @classmethod
    def get_sensor_keys(cls):
        return list(cls.sensor_def.keys())

    def read(self):
        '''
        Read sensor with Adafruit package.
        aqdata is a dict; see sensor_def for keys
        '''
        self.aqdata = self.device.read()
        return self.aqdata

    def get_values(self):
        try:
            self.values = self.read()
        except:
            # I once saw a RuntimeError due to PM25 checksum error and program aborted
            self.values = None
        return self.values

    @classmethod
    def get_str_value(cls, key, value):
        '''
        Format sensor value according to sensor_def.
        :param key: name of value, e.g., temp_c
        :param value: numeric value from the sensor
        :return: example: '15.0 C' for temperature
        '''
        strValue = '{0:{1}} {2}'.format(value, cls.sensor_def[key][2], cls.sensor_def[key][1])
        return strValue

    @classmethod
    def printall(cls, values):
        # iterate over all values returned from device
        for v in values:
            sens_form = cls.sensor_def[v]
            print('{}: {}'.format(sens_form[0], cls.get_str_value(v,values[v])))

def get_device(name='pi'):
    reset_pin = None
    # If you have a GPIO, its not a bad idea to connect it to the RESET pin
    # reset_pin = DigitalInOut(board.G0)
    # reset_pin.direction = Direction.OUTPUT
    # reset_pin.value = False


    # For use with a computer running Windows:
    # import serial
    # uart = serial.Serial("COM30", baudrate=9600, timeout=1)

    # For use with microcontroller board:
    # (Connect the sensor TX pin to the board/computer RX pin)
    # uart = busio.UART(board.TX, board.RX, baudrate=9600)

    # For use with Raspberry Pi/Linux:
    # import serial
    # uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=0.25)

    # For use with USB-to-serial cable:
    # import serial
    # uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.25)

    # Connect to a PM2.5 sensor over UART
    # from adafruit_pm25.uart import PM25_UART
    # pm25 = PM25_UART(uart, reset_pin)

    # Create library object, use 'slow' 100KHz frequency!
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    # Connect to a PM2.5 sensor over I2C
    pm25 = PM25_I2C(i2c, reset_pin)

    return name,pm25

def get_keys(device, known=True):
    '''
    PM25 device returns a dict with the data.
    This function just returns the keys and not the data.
    :param device: PM25 device as returned from get_device()
    :param known: if True, return a list of well-known keys. if False, just return entire set.
    :return: list of keys
    '''
    keys = []
    if known:
        keys = ['pm10 standard', 'pm25 standard', 'pm100 standard',
                'pm10 env', 'pm25 env', 'pm100 env',
                'particles 03um',
                'particles 05um',
                'particles 10um',
                'particles 25um',
                'particles 50um',
                'particles 100um',
            ]
    else:
        keys = [key for key in device]
    return keys

def printall(aqdata):
    '''
    print data, for testing
    '''
    dt_now = dt.datetime.now()
    print("{}".format(dt_now))
    for key in aqdata:
        # SensorValue['pm10 env'] = ('PM1.0 env', '', 'd')
        #sens = SensorValue[key]
        print('{0}: {1}'.format(key,aqdata[key]))

def printit(aqdata):
    '''
    print data, for testing
    '''
    dt_now = dt.datetime.now()
    print("{}".format(dt_now))
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")

if __name__ == '__main__':
    name,pm25 = get_device()
    print("Found PM2.5 sensor on {}, reading data...".format(name))
    while True:
        try:
            aqdata = pm25.read()
            # print(aqdata)
            printall(aqdata)
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue
        time.sleep(15)
