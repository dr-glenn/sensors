# read some sensors, publish with MQTT

import datetime as dt
import time
# ------ LOCAL -------
import pm25
import bme280

if __name__ == '__main__':
    bme_name,bme_vals = bme280.get_values()
    bme280.printit(bme_name,bme_vals)
    pm25_name,pm25_dev = pm25.get_device()
    aqdata = pm25_dev.read()
    #pm25.printit(aqdata)
    pm25.printall(aqdata)
