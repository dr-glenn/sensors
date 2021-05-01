import time
import paho.mqtt.client as paho
broker="iot.eclipse.org"
broker="broker.hivemq.com"
broker="test.mosquitto.org"
MQTT_PORT = 1883

from pi_devices import bme280, pm25

BME_NAME = 'pi_zero/bme280'
PM25_NAME = 'pi_zero/pm25'

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    print("connected with result code: "+str(rc))
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    client.subscribe(BME_NAME)
    client.subscribe(PM25_NAME)
    #client.subscribe("$SYS/#") # some interesting things

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
#bme_name,bme280_dev = bme280.get_device()
#pm25_name,pm25_dev = pm25.get_device()
bme280_dev = bme280.BME280('pi_zero')
pm25_dev = pm25.PM25('pi_zero')

#####
print("connecting to broker %s" %broker)
client.connect(broker, MQTT_PORT)
client.loop_start() #start loop to process received messages
#print("subscribing ")
#client.subscribe(BME_NAME)#subscribe
time.sleep(2)

for i in range(5):
    print("publishing ")
    #temp = bme280_dev.temperature
    #humid = bme280_dev.relative_humidity
    #press = bme280_dev.pressure
    bme_values = bme280_dev.get_values()
    temp = bme_values['temp_c']
    humid = bme_values['rel_hum']
    press = bme_values['pressure']
    client.publish(BME_NAME,"%.1f, %.1f%%, %.1fmb" %(float(temp),float(humid),float(press)))
    aqdata = pm25_dev.get_values()
    #        keys = ['pm10 standard', 'pm25 standard', 'pm100 standard',
    client.publish(PM25_NAME, "PM1.0: {}, PM2.5: {}, PM10.0: {}".format(aqdata['pm10 env'],
                aqdata['pm25 env'], aqdata['pm100 env']))

    time.sleep(5)
client.disconnect()
