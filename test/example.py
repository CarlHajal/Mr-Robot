import sys 
import threading
from time import sleep
import time
import inspect
from collections import deque

from automation.sensor import Sensor
from automation.conveyor import Conveyor
from automation.pneumatic import Pneumatic
from automation.MachineMotion import MachineMotion
from automation.estop import EStop
import settings

systemIPAddress = "192.168.7.2"

print("initializing sensors")
box_exit_sensor = Sensor("Box Exit", ipAddress=systemIPAddress, networkId=1, pin=3)
box_exit2_sensor = Sensor("Box Exit2", ipAddress=systemIPAddress, networkId=1, pin=2)
box_enter_sensor = Sensor("Box Enter", ipAddress=systemIPAddress, networkId=1, pin=1)
box_fill_sensor = Sensor("Box Fill", ipAddress=systemIPAddress, networkId=1, pin=0)

print("initializing pneumatics")
gate_pneumatic = Pneumatic("Gate Pneumatic", ipAddress=systemIPAddress, networkId=1, pushPin=0, pullPin=1)
clamp_pneumatic = Pneumatic("Gate Pneumatic", ipAddress=systemIPAddress, networkId=1, pushPin=2, pullPin=3)

print("initializing conveyors")
mm1 = MachineMotion(systemIPAddress)
infeed_conveyor = Conveyor(name="infeed conveyor", mm = mm1, axis_config=settings.AXIS_1_CONFIG)
outfeed_conveyor = Conveyor(name="outfeed conveyor", mm = mm1,  axis_config=settings.AXIS_1_CONFIG)
transfer_conveyor = Conveyor(name="transfer conveyor", mm = mm1,  axis_config=settings.AXIS_1_CONFIG)

def estop_triggered_cb(status):
    if status == True:
        print("estop triggered")
        mm1.emitStop()
    else:
        print("estop released!")
    
try:
    estop = EStop(mm1, cb=estop_triggered_cb)
    while True:
        box_enter_sensor.wait_for_rising_edge()
        infeed_conveyor.roll()
except KeyboardInterrupt:
    pass