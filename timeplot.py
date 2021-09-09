# create graphs of sensor values
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt

# there are more sensor values, but these are the ones we want
SENSOR_NAMES = ['time', 'PM2_5', 'temp_c', 'humidity', 'pressure']
sensor_devs = {}

class SensorVals:
    def __init__(self,sens_name):
        self.name = sens_name
        self.vals = {}
    def add_value(self, val_name, value):
        if not val_name in self.vals:
            self.vals[val_name] = list()
        self.vals[val_name].append(value)

def log_parse(line):
    values = {}
    fld1 = line.find(':')
    sens_dev = line[:fld1].strip()
    if not sens_dev in sensor_devs:
        sensor_devs[sens_dev] = SensorVals(sens_dev)
        location,computer,sensor = sens_dev.split('/')
        print('{},{},{}'.format(location,computer,sensor))
    ll = line[fld1+1:].strip()
    ff = ll.split(',')
    for f in ff:
        fld_name,fld_val = f.split('=')
        #values[fld_name] = fld_val
        if fld_name == 'time':
            val = fld_val
        else:
            val = float(fld_val)
        sensor_devs[sens_dev].add_value(fld_name,val)

def read_log(fname):
    with open(fname, 'r') as df:
        lines = df.readlines()
    for line in lines:
        log_parse(line)

def main(logfile):
    read_log(logfile)
    # now sensor_devs should be filled
    plt.figure(dpi=100.0, figsize=(6,4))
    fig,axs = plt.subplots(3)
    iplt = 0
    for dev_key in sensor_devs:
        dev = sensor_devs[dev_key]
        print('device = {}'.format(dev.name))
        for key in dev.vals:
            print('  key={} has {} values'.format(key,len(dev.vals[key])))
        if dev_key.find('bme280') >= 0 or dev_key.find('pm25') >= 0:
            vtimes = [dt.datetime.fromisoformat(t) for t in dev.vals['time']]
            axs[iplt].yaxis.set_major_locator(plt.MaxNLocator(4))
            if dev_key.find('bme280') >= 0:
                vals = dev.vals['temp_c']
                axs[iplt].plot(vtimes, vals)
                axs[iplt].set_title('Temp C', y=1.0, pad=-14)
                iplt += 1
                vals = dev.vals['humidity']
                axs[iplt].plot(vtimes, vals)
                axs[iplt].set_title('Humidity', y=1.0, pad=-14)
                iplt += 1
            if dev_key.find('pm25') >= 0:
                vals = [int(v) for v in dev.vals['PM2_5']]
                axs[iplt].plot(vtimes, vals)
                axs[iplt].set_title('Air Quality 2.5', y=1.0, pad=-14)
                iplt += 1

    plt.gcf().autofmt_xdate()
    plt.show()

if __name__ == '__main__':
    logfile = 'mqtt_rcv.log'
    main(logfile)
