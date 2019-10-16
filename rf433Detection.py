#!/usr/bin/python
#from gpiozero import MotionSensor
from time import sleep
import paho.mqtt.client as mqtt, time, sys
import os
import re
import threading
import subprocess
from array import array
MQTT_PASSWORD="MY_PASSWORD"
MQTT_USER="MY_USER"

#motion = MotionSensor(4, pull_up=None, active_state=True, sample_rate=4)
RF_STATE_TOPIC="homeassistant/binary_sensor/switch{}/state"
print("Start")
#p = subprocess.Popen(['/home/pi/rc-switch-pi-examples/receivedemo', ''], stdout=subprocess.PIPE, shell=True)
#process.Popen(['/usr/local/bin/receiveRf400', ''], stderr=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
RF_COMMAND="/usr/local/bin/receiveRf400"
#p = subprocess.Popen(['ls', '-l'], stdout=subprocess.PIPE, shell=True)
global popen
global detectedSwitches 
detectedSwitches = array('l')

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.is_connected = True

def on_message(client, userdata, message):
    print("Message")

def publishMotion():
    global detected

serverIp="192.168.1.2"
client = mqtt.Client()
# if you need a username and/or password for mqtt uncomment next line
client.username_pw_set(MQTT_USER, password=MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.is_connected = False
client.loop_start()
client.connect(serverIp) # replace "control_central" with ip address or name of server

def newSwitchDetected(number):
    topic="homeassistant/binary_sensor/switch{}/config".format(number)
    stateTopic="{{\"name\": \"switch{}\", \"state_topic\":\""+RF_STATE_TOPIC+"\" }}"
    stateTopic=stateTopic.format(number, number)
    sys.stdout.write(stateTopic+"\n")
    sys.stdout.write(topic+"\n")
    client.publish(topic,stateTopic, retain=True)

def checkForNewSwitch(number):
    if not number in detectedSwitches:
        sys.stdout.write("New switch: "+str(number)+"\n")
        detectedSwitches.append(number)
        newSwitchDetected(int(number))

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        stdout_line.split()
        splitted=stdout_line.split()
        #sys.stdout.write("Length: "+str(len(splitted)))
        if len(splitted) == 2:
            checkForNewSwitch(int(splitted[0]))
            sys.stdout.write("Switch"+splitted[0]+" Value:"+splitted[1]+"\n")
            topic=RF_STATE_TOPIC.format(splitted[0])
            client.publish(topic,"ON" if splitted[1] == "1" else "OFF", retain=True)
            #client.publish(topic,splitted[1], retain=True)
        #yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def cleanup():
#client.publish("homeassistant/binary_sensor/raspbiMotion/config",'', retain=True)
    client.loop_stop()
    client.disconnect()
    popen.kill()

#execute("/home/pi/rc-switch-pi-examples/receive")
for path in execute([RF_COMMAND,""]):
    print(path, end="")
while True:
    checkForNewSwitch(int("10"))
    time.sleep(1)

atexit.register(cleanup)

