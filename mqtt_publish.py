import platform
import time
import random
import datetime as dt
import json
import RPi.GPIO as GPIO
import paho.mqtt.client as paho
import I2C_LCD_driver   # for LCD1602 device with backpack
import myconfig as cfg

ANONYMOUS=False
if ANONYMOUS:
    #broker="iot.eclipse.org"
    #broker="broker.hivemq.com"
    broker="test.mosquitto.org"
    MQTT_PORT = 1883
else:
    broker = cfg.MQTT_BROKER
    MQTT_PORT = cfg.MQTT_PORT

GPIO.setmode(GPIO.BCM)

from pi_devices import bme280, pm25

HOME_NAME = 'gn_home'
#SYS_NAME  = 'pi_zero'
SYS_NAME  = platform.node()
BME_NAME  = 'bme280'
PM25_NAME = 'pm25'

BME_TOPIC  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME)
PM25_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME)
BME_TOPIC_JSON = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME+'/J')
PM25_TOPIC_JSON = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME+'/J')

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    print("connected with result code: "+str(rc), flush=True)
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    #client.subscribe(BME_NAME)
    #client.subscribe(PM25_NAME)
    #client.subscribe("$SYS/#") # some interesting things

def on_publish(client, userdata, mID):
    tstamp = dt.datetime.now()
    tstampStr = tstamp.strftime('%Y-%m-%dT%H:%M:%S%z')
    print("publish msg ID={} at {}".format(int(mID),tstampStr), flush=True)

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message = %s" %str(message.payload.decode("utf-8")))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected MQTT disconnection. Might auto-reconnect.", flush=True)

client= paho.Client("gdn-client-{:04d}".format(random.randrange(1000))) #create client object
if not ANONYMOUS:
    #client.tls_set(tls_version=paho.ssl.PROTOCOL_TLS)
    client.tls_set()
    client.username_pw_set(cfg.MQTT_USERNAME, cfg.MQTT_PASSWORD)
else:
    pass


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

HAS_LCD = True
lcdHourOn  = 7   # backlight turns on at this hour
lcdHourOff = 23 # don't want that bright backlight during the night
mylcd = None

if HAS_LCD:
    mylcd = I2C_LCD_driver.lcd()
    mylcd.backlight(0)  # start with backlight off
else:
    # no LCD hooked up
    mylcd = None

lcd_msgs = [None, None, None, None] # up to 4 rows on LCD display
lcd_row_idx = [0, 0, 0, 0]
def lcd_queue(row, msgs):
    '''
    Queue a series of messages for a designated row.
    Display the first message. Use a timer to display others.
    :param row: row integer, starting with 1
    :param msgs: a list of messages
    If msgs is None or empty list, then clear the row
    :return: nothing
    '''
    global mylcd, lcd_msgs
    if not mylcd:
        return
    if not msgs:
        lcd_msgs[row-1] = None
        mylcd.lcd_display_string('', row)
        return
    else:
        lcd_msgs[row-1] = msgs
        mylcd.lcd_display_string(msgs[0], row)
        return

def lcd_queue_change(row):
    global lcd_msgs
    if lcd_msgs[row-1]:
        msg_idx = lcd_row_idx[row-1]
        
def lcd_show(timestr, obsstr, override=False):
    '''
    Display temp and humid on local LCD display.
    '''
    global mylcd, lcdHourOn, lcdHourOff
    if not mylcd:
        return
    # turn off backlight at night
    hour = int(timestr.split(':')[0])
    if override or (hour >= lcdHourOn and hour < lcdHourOff):
        # Show time on line 1, T,H on line 2
        mylcd.lcd_clear()   # otherwise you may see some digits from previous reading
        mylcd.lcd_display_string(timestr, 1)
        #obsstr += "T=%.1f%sF, " % (1.8*float(temp22)+32.0, chr(223))
        #obsstr += "H=%d%%" % int(hum22)
        mylcd.lcd_display_string(obsstr, 2)
        #print('time={}, obs={}'.format(timestr,obsstr), flush=True)
    else:
        # night time, make it dark
        mylcd.backlight(0)

from threading import Timer

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

'''
Example: with repeat time of 1 second, if we issue time.sleep(5), we expectdummyfn to run 4 or manybe 5 times
def dummyfn(msg="foo"):
    print(msg)

timer = RepeatTimer(1, dummyfn)
timer.start()
time.sleep(5)
timer.cancel()
'''

def sleep(seconds, pm25_dev=None):
    '''
    Sleep the entire program for 'seconds'.
    But also sleep the PM25 device and then wake it before allowing program to proceed.
    If seconds==0, then just make sure to bring PM25 out of sleep.
    '''
    if not pm25_dev:
        # Assume pm25 does not exist or that it is never put to sleep
        time.sleep(seconds)
    else:
        if seconds > pm25.PM25_WAKE_TIME:
            pm25_dev.sleep()    # extend the life of PM25 (normally around 1 year)
            time.sleep(seconds-pm25.PM25_WAKE_TIME)
        pm25_dev.wake()
        time.sleep(pm25.PM25_WAKE_TIME) # wait for device to be truly ready

#####
print("connecting to broker %s" %broker)
client.connect(broker, MQTT_PORT)
# if you use loop_start, then client automatically reconnects if disconencted
client.loop_start() #start loop to process received messages
#print("subscribing ")
#client.subscribe(BME_NAME)#subscribe
sleep(0, pm25_dev)   # wait for connect to setup

while True:
    print("publishing ")
    tstamp = dt.datetime.now()
    tstampStr = tstamp.strftime('%Y-%m-%dT%H:%M:%S%z')
    #temp = bme280_dev.temperature
    #humid = bme280_dev.relative_humidity
    #press = bme280_dev.pressure
    bme_values = bme280_dev.get_values()
    temp = bme_values['temp_c']
    tempf = temp*1.8 + 32.0
    humid = bme_values['rel_hum']
    press = bme_values['pressure']
    temp_str = '{:.1f}'.format(float(temp))
    tempf_str = '{:.1f}'.format(float(tempf))
    humid_str = '{:.1f}'.format(float(humid))
    press_str = '{:.1f}'.format(float(press))
    client.publish(BME_TOPIC,"time={},temp_c={},humidity={},pressure={}".format(
        tstampStr,temp_str,humid_str,press_str))
    bme_json = {'temp_c':temp_str, 'temp_f':tempf_str, 'humidity':humid_str, 'pressure':press_str}
    client.publish(BME_TOPIC_JSON, json.dumps(bme_json))
    aqdata = pm25_dev.get_values()
    #        keys = ['pm10 standard', 'pm25 standard', 'pm100 standard',
    if aqdata:
        client.publish(PM25_TOPIC, "time={},PM1_0={},PM2_5={},PM10_0={}".format(
            tstampStr,aqdata['pm10 env'], aqdata['pm25 env'], aqdata['pm100 env']))
        aq_json = {'pm10': aqdata['pm10 env'], 'pm25': aqdata['pm25 env'], 'pm100': aqdata['pm100 env']}
        client.publish(PM25_TOPIC_JSON, json.dumps(aq_json))
    else:
        print('PM25 device returned None (probably threw exception)')
    timestr = time.strftime("%H:%M:%S")
    obsstr = 'T:{:.1f}{}F, AQ={:d}'.format(1.8*temp+32,chr(223),int(aqdata['pm25 env']))
    lcd_show(timestr, obsstr, override=False)


    #time.sleep(300) # 5 minutes
    sleep(300,pm25_dev) # 5 minutes and suspend the PM25
client.disconnect()
