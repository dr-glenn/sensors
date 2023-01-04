import os
import sys
import io
import time
import random
import paho.mqtt.client as paho
import json
import csv
import myconfig as cfg
import logging
from logging.handlers import RotatingFileHandler,TimedRotatingFileHandler
from MyLogger import mylogger

'''
How to write a TimedRotating log file with a header and CSV content?
https://stackoverflow.com/questions/2363731/append-new-row-to-old-csv-file-python
https://stackoverflow.com/questions/19765139/what-is-the-proper-way-to-do-logging-in-csv-file
https://stackoverflow.com/questions/27840094/write-a-header-at-every-logfile-that-is-created-with-a-time-rotating-logger
'''

logger = logging.getLogger(__name__)
# if you don't assign a formatter, then the log file is totally free-form - whatever you print to it
defFormatter = logging.Formatter('%(levelname)s: %(message)s')
#fileHandler = RotatingFileHandler('mqtt_rcv.log', maxBytes=50000, backupCount=3)
fileHandler = TimedRotatingFileHandler('mqtt_rcv.log', when='midnight', interval=1, backupCount=7)
logger.addHandler(fileHandler)
logger.setLevel(logging.INFO)

# omit pm10 and pm100
fields = ['time','topic','pm25','temp_f','humidity','pressure']
# create time-rotating log handler for CSV file with header
csvFile = 'my_sensors.csv'

"""
class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    '''
    Use this class to override doRollover so that a header can be written at the top of the logfile.
    There will also be a custom Formatter for writing CSV records to the logfile.
    '''
    def __init__(self, logfile, when, interval=1):
        super(MyTimedRotatingFileHandler, self).__init__(logfile, when, interval)
        self._header = ""
        self._log = None

    def doRollover(self):
        '''
        TODO: this method writes the header to the logger instance, thereby invoking the custom
        formatter. The formatter does a csv.DictWriter.writerow - uh oh! We'd really prefer to
        do DictWriter.writeheader. So I have some squirrelly code in configureHeaderWriter,
        but I'd like a better implementation.
        '''
        super(MyTimedRotatingFileHandler, self).doRollover()
        if self._log is not None and self._header != "":
            self._log.info(self._header)
    '''
    def setHeader(self, header):
        self._header = header
    '''

    def configureHeaderWriter(self, header, log):
        '''
        Since this is a CSV writer, the header should be a list of field names.
        The field names must be written in order so that when DictWriter.writerow() is called,
        the fields are correctly named.
        '''
        if isinstance(header,(list,tuple)):
            # quote each field name, write comma separated
            #header = ','.join(f'"{w}"' for w in header)
            headDict = { f'{w}':f'{w}' for w in header}
        else:
            # TODO: raise exception
            headDict = str(header)
        self._header = headDict
        self._log = log

class CsvFormatter(logging.Formatter):
    def __init__(self, fieldnames):
        super().__init__()
        self.fieldnames = fieldnames
        self.output = io.StringIO()
        self.writer = csv.DictWriter(self.output, self.fieldnames, extrasaction='ignore', quoting=csv.QUOTE_ALL)

    def format(self, record):
        #self.writer.writerow([record.levelname, record.msg])
        self.writer.writerow(record.msg)
        data = self.output.getvalue()
        self.output.truncate(0)
        self.output.seek(0)
        return data.strip()

csvHandler = MyTimedRotatingFileHandler(csvFile, when='midnight')
#form = '%(asctime)s %(name)s %(levelname)s: %(message)s'
form = '%(message)s'
csvFormatter = logging.Formatter(form)
#csvHandler.setFormatter(csvFormatter)
csvHandler.setFormatter(CsvFormatter(fields))

# create logger
csvLog = logging.getLogger('MyCSV')
csvHandler.configureHeaderWriter(fields, csvLog)
csvLog.addHandler(csvHandler)
csvLog.setLevel(logging.INFO)
"""

csvLogger = mylogger.CsvLogger('MyCSV', csvFile, fields)
csvLog = csvLogger.getLogger('MyCSV')

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
SYS_NAME  = 'gn-pi-zero-2'
BME_NAME  = 'bme280'
PM25_NAME = 'pm25'

#DEV_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,'#')
DEV_TOPIC = '{}/{}/{}'.format(HOME_NAME,'+','+')
DEV_TOPIC_JSON = '{}/{}/{}/J'.format(HOME_NAME,SYS_NAME,'+')
BME_TOPIC  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME)
PM25_TOPIC = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME)
BME_TOPIC_JSON  = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,BME_NAME+'/J')
PM25_TOPIC_JSON = '{}/{}/{}'.format(HOME_NAME,SYS_NAME,PM25_NAME+'/J')

# callbacks for mqtt
def on_connect(client, userdata, flags, rc):
    #print("connected with result code: "+str(rc))
    # subscribe within the on_connect function,
    # so that if connection is lost, subscription will get renewed.
    #client.subscribe(DEV_TOPIC)
    client.subscribe(DEV_TOPIC_JSON)
    #client.subscribe(BME_TOPIC_JSON)
    #client.subscribe(PM25_TOPIC)
    #client.subscribe("$SYS/#")

def on_message(client, userdata, message):
    time.sleep(1)
    #print("received message = %s" %str(message.payload.decode("utf-8")))
    msg = message.payload.decode("utf-8")
    # msg is always a string, so I have to identify json and convert it
    #logger.info('message is {}'.format(type(msg)))
    if msg.startswith('{'):
        mydict = json.loads(msg)
        mydict['topic'] = message.topic
        logger.info(json.dumps(mydict))
        csvLog.info(mydict)
    else:
        logger.info(str(message.topic)+': '+str(message.payload.decode("utf-8")))

def on_message_json(client, userdata, message):
    time.sleep(1)
    #print("received message = %s" %str(message.payload.decode("utf-8")))
    logger.info(str(message.topic)+', '+str(message.payload.decode("utf-8")))

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
        client.on_message = on_message
        main(client, broker)
    except KeyboardInterrupt:
        print('exit program')
        client.disconnect()
        client.loop_stop()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
