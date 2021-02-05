from time import sleep
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as MQTTsubscribe
import sys

import logging
log = logging.getLogger(__name__)

class EStop():
    
    def eStopCallback(self, client, userData, msg):
        eStopState = msg.payload
        log.info("{} received estop message {}".format(self.mm.IP, msg.payload))      
        if eStopState == "true":
            self._isTriggered = True   
        else:
            self._isTriggered = False
        if self.cb_args:
            self.cb(self.isTriggered, args = self.cb_args)
        else:
            self.cb(self.isTriggered)

        
    def __onConnect(self, client, userData, flags, rc):
        if rc == 0:
            topic = 'estop/status'
            self.sensorClient.subscribe(topic)
            self.connected = True
            log.info("Estop connected")
        return
    
    def __init__(self, mm, cb=None, cb_args=None):
        self.mm = mm
        self._isTriggered = False       
        self.connected=False
        self.sensorClient = None
        self.sensorClient = mqtt.Client()
        self.sensorClient.on_connect = self.__onConnect
        self.sensorClient.on_message = self.eStopCallback
        self.sensorClient.connect(mm.IP)
        self.sensorClient.loop_start()
        self.cb = cb
        self.cb_args = cb_args
        
        while self.connected == False:
            sys.stdout.write("..")
            sleep(0.2)

    def isTriggered(self):
        return self._isTriggered
    
    def release(self):
        self.messageReceived = False
        self.mm.releaseEstop()
        self.mm.resetSystem()
        sleep(1)
        print("{} estop triggered == {}".format(self.mm.name, self._isTriggered))
        isReleased = not self._isTriggered
        return isReleased
   
