import logging
log = logging.getLogger(__name__)
from time import sleep, time
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as MQTTsubscribe
import sys


class Encoder():
    def count2pos(self, count):
        if not count:
            return "not initialized"
        return (count - self.initialValue)/3600*self.mechGain
        
    
    def __getSpeed(self):
        
        if(not self.pos):
            return "Not initialized"
        
        lastReadTime = self.lastReadTime if self.lastReadTime else self.t0
        thisReadTime = time()
        lastReadPos = self.lastReadPos if self.lastReadPos else self.count2pos(self.value)
        thisReadPos = self.pos 
        
        self.speed = abs(thisReadPos - lastReadPos)/(thisReadTime-lastReadTime)
        
        self.lastReadTime = thisReadTime
        self.lastReadPos = thisReadPos
        
        log.info("speed = " + self.speed)
        
        return self.speed
    
    def __repr__(self):
        out = {"inital value":self.initialValue,"current value":self.value, "current pos":self.pos, "speed":self.speed}
        outStr = "\t".join([str(k) + ":" + str(v) for (k,v) in out.items()])
        return outStr
    
    def __onConnect(self, client, userData, flags, rc):
        if rc == 0:
            topic = 'devices/encoder/' + str(self.encoderId) + '/realtime-position'
            self.sensorClient.subscribe(topic)
            self.t0 = time()
            self.connected = True
        return
    
    def __onMessage(self, client, userData, msg):
        if not self.initialValue:
            self.initialValue=float(msg.payload)
        self.value = float(msg.payload)
        self.pos = self.count2pos(self.value)
        self.speed = self.__getSpeed()
        return
    
    def __init__(self, mm, name, encoderId, mechGain = None, cb=None):
        self.lastReadTime = False
        self.lastReadPos = False
        self.t0 = False
        self.value = False
        self.pos = False
        self.initialValue = False
        self.speed = False
        self.encoderId = encoderId
        self.name = name
        self.cb = cb
        self.mechGain = mechGain
        self.connected = False
        self.sensorClient = None
        self.sensorClient = mqtt.Client()
        self.sensorClient.on_connect = self.__onConnect
        self.sensorClient.on_message = self.__onMessage
        self.sensorClient.connect(mm.IP)
        self.sensorClient.loop_start()
        
        while self.connected == False:
            sys.stdout.write("..")
        log.info(self.name + " mqtt client connected!")
        

