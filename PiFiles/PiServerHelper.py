from MoistureSensors import MoistureSensor
import json, codecs
from bson import json_util
import operator
import datetime
import time
import urllib
import urllib2

class PiServerHelper(object):
    def __init__(self):
        self.sensorMap = {}  # map to store the readings
        self.threshold = 100  # amount of readings to collect
        self.intervals = 30  # Intervals to Poll the sensors
        self.pollMode = False  # poll or interrupt mode
        self.numSensors = 5  # number of sensors
        self.outsideMode = False  # is the cluster outside
        self.temperature = 0
        self.numReadings = 0
        self.timeToWait = 45
        self.clusterName = "ORIGINAL_PI"
        urlName = 'http://moisty.herokuapp.com/'
        self.urls = {}
        self.urls["head"] = urlName+'cluster_heads.json'
        self.urls["sensors"] = urlName+'moisture_sensors.json'
        self.urls["readings"] = urlName+'moisture_readings.json'
        self.addressSet = set()
        
        
    def Setup(self, filename, alreadySetup):
        lines = [line.rstrip('\n\r') for line in open(filename)]
        addresses = []
        self.addressSet = set()
        names = []
        for line in lines[1:]:
            info = line.split(',')
            self.addressSet.add(info[0])
            names.append(info[1])
        addresses = list(self.addressSet)

        payload = {"bluetooth_address":addresses, "name":names}
  
        self.clusterName = lines[0]
        if not alreadySetup:
            self.initializeCluster()
            self.initializeAddresses(payload)        

    def readable(self, address):
        now = time.mktime(datetime.datetime.now().timetuple())
        #print("got now")
        if address not in self.sensorMap:
            #print("returning true in readable")
            return True;        
        last = time.mktime(self.sensorMap[address].lastTime.timetuple())
        #print("got last time")
        diff = now-last
        #print(diff)
        return diff > self.timeToWait 

    def insertReading(self, id, moistureReading):
        if id not in self.sensorMap:
            self.sensorMap[id] = MoistureSensor()
            self.sensorMap[id].id = id;

        Sensor = self.sensorMap[id]
        Sensor.readings.append(moistureReading)
        now = datetime.datetime.now()
        Sensor.lastTime = now;
        Sensor.timestamps.append(now.strftime("%Y-%m-%d %H:%M:%S"))
        Sensor.numReadings += 1
        self.numReadings += 1


    def clearReadings(self, address):
        self.numReadings = self.numReadings - self.sensorMap[address].clear()


    def readingsToJson(self):
        sensorData = {}
        for key in self.sensorMap:
            if(self.sensorMap[key].numReadings != 0):
                sensorData[key] = self.sensorMap[key].__dict__
        return sensorData

    def initializeCluster(self):
        clusters = {}
        clusters["cluster_head_name"] = self.clusterName
        data = urllib.urlencode(clusters)
        req = urllib2.Request(self.urls["head"], data)
        try:
            response = urllib2.urlopen(req, timeout = 5)
            the_page = response.read()
            print(the_page)
        except:
            print("Error Initializing Cluster")

    def initializeAddresses(self, addresses):
        try:
            addresses["cluster_head_name"] = self.clusterName
            data = urllib.urlencode(addresses)
            req = urllib2.Request(self.urls["sensors"], data)
            response = urllib2.urlopen(req, timeout = 5)
            the_page = response.read()
            print(the_page)
        except:
            print("Error Initializing Addresses")

    def sendReading(self):
        values = {}
        values = self.readingsToJson()
        sent = False
        for key in values:
            payload = values[key]
            payload["cluster_head_name"] = self.clusterName
            #print(payload)
            try:
                data = urllib.urlencode(payload)
                req = urllib2.Request(self.urls["readings"], data)
                response = urllib2.urlopen(req, timeout = 5)
                the_page = response.read()
                #print("line 120" + the_page)
                if the_page != "1":
                    #print("line 122")
                    return False
                else:
                    #print("line 125")
                    #print(values[key])
                    self.clearReadings(values[key]["id"])
            except:
                logger.error('Failed to do something: ' + str(e))
                return False
        return True
            

    def sendBrokenSensor(self):
        return 1

    def findMode(self, freqMap):
        try:
           return max(freqMap.iteritems(), key=operator.itemgetter(1))[0]
        except:
            return -1

    def concatOutput(self, process):
        output = ''
        for line in process.stdout:
            if line[0] == 'o':
                line = line.translate(None, ':')
                actual = line[32:-1]
                actual = actual.decode("hex")
                output = output + actual

        output = output.translate(None, '\0')
        return output

    def parseOutput(self, toParse):
        readings = []
        mode = {}
        for i in range(0, len(toParse)):
            if toParse[i] == 's':
                index = i + 4
                size = int(toParse[i + 1:index])
                reading = toParse[index:index + size]
                readings.append(reading)
                i = index + size
                if reading not in mode:
                    mode[reading] = 0
                    mode[reading] = mode[reading] + 1

        return self.findMode(mode)
