"""
Example sketch to connect to PM2.5 sensor with either I2C or UART.
"""

# pylint: disable=unused-import
import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
import datetime as dt

def get_device():
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

    return pm25

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
    pm25 = get_device()
    print("Found PM2.5 sensor, reading data...")
    while True:
        try:
            aqdata = pm25.read()
            # print(aqdata)
            printit(aqdata)
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue
        time.sleep(15)
