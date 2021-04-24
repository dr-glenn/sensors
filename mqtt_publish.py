import time
import paho.mqtt.client as paho
broker="iot.eclipse.org"
broker="broker.hivemq.com"
broker="test.mosquitto.org"
MQTT_PORT = 1883

import bme280
import pm25

BME_NAME = 'pi_zero/bme280'
PM25_NAME = 'pi_zero/pm25'

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    print("connected with result code: "+str(rc))
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    client.subscribe(BME_NAME)
    client.subscribe(PM25_NAME)
    #client.subscribe("$SYS/#")

def on_publish(client, userdata, mID):
    print("publish msg ID=%d"%(int(mID)))

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message = %s" %str(message.payload.decode("utf-8")))

client= paho.Client("gdn-client-001") #create client object

###### Bind functions to callback
client.on_connect = on_connect
client.on_publish = on_publish #assign function to callback
client.on_message=on_message

#####
bme_name,bme280_dev = bme280.get_device()
pm25_name,pm25_dev = pm25.get_device()

#####
print("connecting to broker %s" %broker)
client.connect(broker, MQTT_PORT)
client.loop_start() #start loop to process received messages
#print("subscribing ")
#client.subscribe(BME_NAME)#subscribe
time.sleep(2)
print("publishing ")
temp = bme280_dev.temperature
humid = bme280_dev.relative_humidity
press = bme280_dev.pressure
client.publish(BME_NAME,"%.1f, %.1f%%, %.1fmb" %(float(temp),float(humid),float(press)))
aqdata = pm25_dev.read()
#        keys = ['pm10 standard', 'pm25 standard', 'pm100 standard',
client.publish(PM25_NAME, "PM1.0: {}, PM2.5: {}, PM10.0: {}".format(aqdata['pm10 env'],
            aqdata['pm25 env'], aqdata['pm100 env']))

time.sleep(4)
client.disconnect()
client.loop_stop()

