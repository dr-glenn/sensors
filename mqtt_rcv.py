import os
import sys
import time
import paho.mqtt.client as paho
broker="iot.eclipse.org"
broker="broker.hivemq.com"
broker="test.mosquitto.org"
MQTT_PORT = 1883

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

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message = %s" %str(message.payload.decode("utf-8")))

def main(client, broker, port=MQTT_PORT):
    msg_loop = True

    #####
    print("connecting to broker %s" %broker)
    client.connect(broker, port)
    client.loop_start() #start loop to process received messages
    while msg_loop:
        time.sleep(30)
    #print("subscribing ")
    #client.subscribe("house/temp1")#subscribe
    #time.sleep(60)

if __name__ == '__main__':
    try:
        client= paho.Client("gdn-client-002") #create client object
        ###### Bind functions to callback
        client.on_connect = on_connect
        client.on_message=on_message
        main(client, broker)
    except KeyboardInterrupt:
        print('exit program')
        client.disconnect()
        client.loop_stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
