import os
import sys
import time
import random
import paho.mqtt.client as paho
import myconfig as cfg
import logging
from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler

logger = logging.getLogger(__name__)
defFormatter = logging.Formatter('%(levelname)s: %(message)s')
#fileHandler = RotatingFileHandler('mqtt_rcv.log', maxBytes=50000, backupCount=3)
fileHandler = TimedRotatingFileHandler('mqtt_rcv.log', when='midnight', interval=1, backupCount=7)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

ANONYMOUS=False
if ANONYMOUS:
    #broker="iot.eclipse.org"
    #broker="broker.hivemq.com"
    broker="test.mosquitto.org"
    MQTT_PORT = 1883
else:
    broker = cfg.MQTT_BROKER
    MQTT_PORT = cfg.MQTT_PORT

#BME_NAME = 'pi_zero/bme280'
#PM25_NAME = 'pi_zero/pm25'


HOME_NAME = 'gn_home'
SYS_NAME  = 'gn-pi-zero-1'
BME_NAME  = 'bme280'
PM25_NAME = 'pm25'

#DEV_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,'#')
DEV_TOPIC = '{}/{}/{}'.format(HOME_NAME,'+','+')
BME_TOPIC  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME)
PM25_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME)
BME_TOPIC_JSON  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME+'/J')
PM25_TOPIC_JSON = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME+'/J')

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    #print("connected with result code: "+str(rc))
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    client.subscribe(DEV_TOPIC)
    #client.subscribe(BME_TOPIC_JSON)
    #client.subscribe(PM25_TOPIC)
    #client.subscribe("$SYS/#")

def on_message(client, userdata, message):
    time.sleep(1)
    #print("received message = %s" %str(message.payload.decode("utf-8")))
    logger.info(str(message.topic)+': '+str(message.payload.decode("utf-8")))

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
        client= paho.Client("gdn-client-{:04d}".format(random.randrange(1000))) #create client object
        if not ANONYMOUS:
            #client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
            client.tls_set()
            client.username_pw_set(cfg.MQTT_USERNAME, cfg.MQTT_PASSWORD)
        else:
            pass
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
