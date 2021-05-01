# read some sensors, publish with MQTT
# This example uses the class definitions of Devices, PM25 and BME280.

# ------ LOCAL -------
from pi_devices import bme280, pm25

if __name__ == '__main__':
    bme = bme280.BME280('pi_zero')
    vals = bme.get_values()
    bme.printall(vals)

    pm25 = pm25.PM25('pi_zero')
    vals = pm25.get_values()
    pm25.printall(vals)
