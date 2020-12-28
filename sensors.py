# read some sensors, publish with MQTT

import datetime as dt
import time
# ------ LOCAL -------
import pm25
import bme280

if __name__ == '__main__':
    dev_bme280 = bme280.get_device()
    bme280.printit(dev_bme280)
    dev_pm25 = pm25.get_device()
    aqdata = dev_pm25.read()
    pm25.printit(aqdata)
