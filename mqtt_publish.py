import time
import datetime as dt
import RPi.GPIO as GPIO
import paho.mqtt.client as paho

#broker="iot.eclipse.org"
#broker="broker.hivemq.com"
broker="test.mosquitto.org"
MQTT_PORT = 1883

GPIO.setmode(GPIO.BCM)

from pi_devices import bme280, pm25

HOME_NAME = 'gn_home'
SYS_NAME  = 'pi_zero'
BME_NAME  = 'bme280'
PM25_NAME = 'pm25'

BME_TOPIC  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME)
PM25_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME)

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    print("connected with result code: "+str(rc))
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    #client.subscribe(BME_NAME)
    #client.subscribe(PM25_NAME)
    #client.subscribe("$SYS/#") # some interesting things

def on_publish(client, userdata, mID):
    tstamp = dt.datetime.now()
    tstampStr = tstamp.strftime('%Y-%m-%dT%H:%M:%S%z')
    print("publish msg ID={} at {}".format(int(mID),tstampStr))

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message = %s" %str(message.payload.decode("utf-8")))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Might auto-reconnect.")

client= paho.Client("gdn-client-001") #create client object

###### Bind functions to callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish #assign function to callback
client.on_message=on_message

#####
#bme_name,bme280_dev = bme280.get_device()
#pm25_name,pm25_dev = pm25.get_device()
bme280_dev = bme280.BME280('pi_zero')
pm25_dev = pm25.PM25('pi_zero')

#####
print("connecting to broker %s" %broker)
client.connect(broker, MQTT_PORT)
# if you use loop_start, then client automatically reconnects if disconencted
client.loop_start() #start loop to process received messages
#print("subscribing ")
#client.subscribe(BME_NAME)#subscribe
time.sleep(4)   # wait for connect to setup

def sleep(seconds, pm25_dev):
    pm25_dev.sleep()    # extend the life of PM25 (normally around 1 year)
    time.sleep(seconds-pm25.PM25_WAKE_TIME)
    pm25_dev.wake()
    time.sleep(pm25.PM25_WAKE_TIME)

while True:
    print("publishing ")
    tstamp = dt.datetime.now()
    tstampStr = tstamp.strftime('%Y-%m-%dT%H:%M:%S%z')
    #temp = bme280_dev.temperature
    #humid = bme280_dev.relative_humidity
    #press = bme280_dev.pressure
    bme_values = bme280_dev.get_values()
    temp = bme_values['temp_c']
    humid = bme_values['rel_hum']
    press = bme_values['pressure']
    client.publish(BME_TOPIC,"time={},temp_c={:.1f},humidity={:.1f},pressure={:.1f}".format(
        tstampStr,float(temp),float(humid),float(press)))
    aqdata = pm25_dev.get_values()
    #        keys = ['pm10 standard', 'pm25 standard', 'pm100 standard',
    if aqdata:
        client.publish(PM25_TOPIC, "time={},PM1_0={},PM2_5={},PM10_0={}".format(
            tstampStr,aqdata['pm10 env'], aqdata['pm25 env'], aqdata['pm100 env']))
    else:
        print('PM25 device returned None (probably threw exception)')

    #time.sleep(300) # 5 minutes
    sleep(300,pm25_dev) # 5 minutes and suspend the PM25
client.disconnect()
