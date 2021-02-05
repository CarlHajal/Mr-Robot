
import logging
log = logging.getLogger(__name__)

from automation.encoder import Encoder
import settings
import threading
from time import time, sleep

#all classes that inherit Actuator will have their 'start' method invoked during package initialization
class Actuator():
    pass

class Conveyor(Actuator):   
    
    def __init__(self, mm, axis, uStep, gain, direction, speed, name):
        log.info("Initializing " + name + " on " + mm.name + " drive " + str(axis))
        self.axis = axis
        self.name = name
        self.mm = mm
        self.conveyorAcceleration = settings.DEFAULT_ACCELERATION
        self.conveyorSpeed = settings.DEFAULT_SPEED

        mm.configAxis(axis, uStep, gain)

        if direction == "positive":
            self.speed = speed
        elif direction == "negative":
            self.speed = speed * -1
    
    def start(self):
        pass
 
    def roll(self):
        self.mm.setContinuousMove(self.axis, self.speed, self.conveyorAcceleration)
        
    def stop(self):
        self.mm.stopContinuousMove(self.axis, 10000)
        


class Blades(Actuator):
    
    bladeSpeed =  settings.DEFAULT_SPEED
    bladeAcceleration = settings.DEFAULT_ACCELERATION
    spinning = False
    checkStall = False
    
    #ready = True
    def __init__(self, mm, axis1, enc1, axis2, enc2, uStep, gain, direction, name, stackLight):
        log.info("Initalizing " + name + " on " + mm.name + " on drive " + str(axis1) + " and " + str(axis2))
        self.axis1 = axis1  
        self.axis2 = axis2  #Axis 2 flips direction relative to axis 1
        self.enc1 = Encoder(mm, "Blade 1", enc1, mechGain = 360, cb=None)
        self.enc2 = Encoder(mm, "Blade 2", enc2, mechGain = 360, cb=None)
        self.blade1Stall = False
        self.blade2Stall = False
        self.name = name
        self.mm = mm
        self.direction = direction
        self.stackLight = stackLight
        
        mm.configAxis(axis1, uStep, gain)
        mm.configAxis(axis2, uStep, gain)

        if direction == "positive":
            self.speed = self.bladeSpeed
        elif direction == "negative":
            self.speed = self.bladeSpeed * -1
    
    def start(self):
        if settings.MONITOR_BLADE_STALLS:
            log.info("Encoders monitoring blade stall")
            self.bladeMonitorThread = threading.Thread(target=self.bladeMonitor)
            self.bladeMonitorThread.daemon = True
            self.bladeMonitorThread.start()

        else:
            log.warning("WARNING: Blade stall turned off")
        
        
    def bladeMonitor(self):
        underSpeedCount = 0
        while(True):
            enc1Speed = self.enc1.speed
            enc2Speed = self.enc2.speed
            if enc1Speed < 0.8* self.bladeSpeed:
                underSpeedCount = underSpeedCount + 1
                if underSpeedCount > 2:
                    self.stackLight.setYellow()
                    log.warning("Stall detected on " + self.name)
                    self.restartBlades()
                    self.stackLight.setGreen()
            else:
                underSpeedCount = 0

            sleep(0.5)
    
    def restartBlades(self):
        log.warning("Restarting " + self.name)
        self.stop()
        sleep(0.1)
        self.spin()    
            
    
    
    def spin(self):
        self.mm.setContinuousMove(self.axis1, self.speed, self.bladeAcceleration)
        self.mm.setContinuousMove(self.axis2, self.speed*-1, self.bladeAcceleration)

        
    def stop(self):
        self.mm.stopContinuousMove(self.axis1, 3000)
        self.mm.stopContinuousMove(self.axis2, 3000)
                

        
class TransferArm(Actuator):
    
    def __init__(self, mm, axis, uStep, gain, direction):
        log.info("Initializing Transfer Arm on " + mm.name + " on drive " + str(axis))
        self.axis = axis
        self.mm = mm
        self.direction = direction
        self.speed = settings.TRANSFERARMSPEED
        self.accel = settings.TRANSFERARMACCEL
        
        log.warning("Stop conveyor on transfer set to " + str(settings.STOP_ON_TRANSFER))

        mm.configAxis(axis, uStep, gain)
        mm.configAxisDirection(axis, direction)
        
    def start(self):
        pass
        
    def sequence(self):
        if(settings.STOP_ON_TRANSFER):
            self.mm.transferConveyor.stop()
            self.mm.inputConveyor.stop()
            
        self.push()
        self.returnHome()
        self.mm.waitForMotionCompletion()
        
        if (settings.STOP_ON_TRANSFER):
            self.mm.transferConveyor.roll()
            self.mm.inputConveyor.roll()
            


        
    def home(self):
        self.mm.emitHome(self.axis)
        self.mm.waitForMotionCompletion()

    def push(self):
        self.mm.emitAbsoluteMove(self.axis, settings.TRANSFERARMDISTANCE)
        
    def returnHome(self):
        self.mm.emitAbsoluteMove(self.axis, 0)
        
        


