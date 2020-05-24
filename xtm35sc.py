#!/usr/bin/python3

import sys, getopt
import minimalmodbus
import paho.mqtt.client as paho
import time
import json
from datetime import datetime

mqttclient = paho.Client("xtm35sc")

version = "v1.1"
help = "xtm35sc.py address [-h] [-i register] [-r {voltage|frequency|current|power|pf}] [-d deviceport] [-m mqttaddress] [-p mqttport] [-P mqtttopicprefix] [-t mqtttopic] [-j] [-s] [-n] [-v] [-N name] [-w]"
def usage():
	#help = 'xtm35sc.py address -i <register> -r <[voltage,frequency,current,power,pf]> -d <device port> -m <mqtt addr> -p <mqtt port> -t <topic> -n -v'
	print("xtm35sc.py is a Modbus/RS485 driver for xtm35sc energy meter with mqtt publishing option")
	print("xtm35sc.py version",version,"\n")
	print("Usage:",help,"\n")
	print("address         : device address on RS485 bus.")
	print("-h,--help       : display this message.")
	print("-i,--id         : device register by id.")
	print("-j,--json       : display results in json format. Default")
	print("-s,--split      : split result in sub topics.")
	print("-r,--register   : device register by name. This could be \"voltage\",\"frequency\",\"current\",\"power\" or \"pf\".")
	print("-d,--deviceport : deviceport. Default is /dev/ttyUSB0.")
	print("-m,--mqtt       : mqtt brocker address. This enable mqtt message.")
	print("-p,--port       : mqtt brocker port. Default is 1883")
	print("-P,--prefix     : mqtt prefix topic. Default is \"/xtm35sc\"")
	print("-t,--topic      : mqtt topic. Default is \"{PREFIX}/{ADDR}\" and \"{ADDR}\" will be replaced by device address or name if -N.")
	print("-n,--numeric    : display only numeric results. This disable json output")
	print("-N,--name       : add name tag to json")
	print("-v,--verbose    : activate verbose mode.")
	print("-w,--watchdog   : reset watchdog on topic \"{PREFIX}/{ADDR}/watchfog\".\n")

def readFloat(rs485,addr):
	retry = 0
	while (retry<5):
		retry += 1
		try:	
			return rs485.read_float(addr, functioncode=4, numberOfRegisters=2)
		except:
			print('retry',addr)
			time.sleep(0.5)
	print("Can't connect to device address {}".format(addr))
	return -1

def main(argv):

	deviceport = '/dev/ttyUSB0'
	numeric = False
	jsonOutput = True
	split = False
	verbose = False
	mqtt = False
	mqttport = 1883
	mqtttopicprefix = "/xtm35sc"
	mqtttopic = "{PREFIX}/{ADDR}"
	registerid = -1
	register = ""
	name = ""
	watchdog = False
	
	if len(argv)==0:
		print(help)
		sys.exit(2)
	else:
		try:
			address = int(argv[0])
		except:
			print(help)
			usage()
			sys.exit(2)
		
	try:
		opts, args = getopt.getopt(argv[1:],"hi:r:d:P:t:m:p:njsvN:w",["help","id=","register=","deviceport=","prefix=","topic=","mqtt=","port=","numeric","json","split","verbose","name=","watchdog"])
	except getopt.GetoptError:
		print(help)
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-i", "--id"):
			registerid = int(arg)
		elif opt in ("-r", "--register"):
			register = arg.lower()
			registerid = -2
		elif opt in ("-m", "--mqtt"):
			mqtt = arg.lower()
		elif opt in ("-p", "--port"):
			mqttport = int(arg)
		elif opt in ("-P", "--prefix"):
			mqtttopicprefix = arg			
		elif opt in ("-t", "--topic"):
			mqtttopic = arg
		elif opt in ("-n", "--numeric"):
			numeric = True
			jsonOutput = False
		elif opt in ("-j", "--json"):
			jsonOutput = True
			numeric = False
		elif opt in ("-s", "--split"):
			split = True
		elif opt in ("-v", "--verbose"):
			verbose = True
		elif opt in ("-d", "--deviceport"):
			deviceport = arg
		elif opt in ("-N", "--name"):
			name = arg
		elif opt in ("-w", "--watchdog"):
			watchdog = True			

	try:
		rs485 = minimalmodbus.Instrument(deviceport, address)
		rs485.serial.baudrate = 9600
		rs485.serial.bytesize = 8
		rs485.serial.parity = 'E'
		rs485.serial.stopbits = 1
		rs485.serial.timeout = 0.5
		rs485.debug = verbose
		rs485.mode = minimalmodbus.MODE_RTU
	except:
		print("Can't access to dev port",deviceport)
		sys.exit(2)
		
	try:
		if mqtt:
			# mqttclient = paho.Client("xtm35sc")
			# mqttclient.on_publish = on_publish
			mqttclient.connect(mqtt,mqttport)			
			mqtttopic = mqtttopic.replace("{PREFIX}",str(mqtttopicprefix))
			if name:
				mqtttopic = mqtttopic.replace("{ADDR}",name)
			else:
				mqtttopic = mqtttopic.replace("{ADDR}",str(address))
		else:
			mqtttopic = False
	except:
		print("Can't connect to",mqtt,":",mqttport)

	alive = False
	jsonResult = { "time":datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f') }
	if (registerid==-1) or (registerid==0) or (register=="voltage"):
		voltage = '{0:.1f}'.format(readFloat(rs485,0))
		if voltage!='-1.0':
			alive = True
			if numeric:
				print(voltage)
			else:
				print('Voltage: {} Volts'.format(voltage))
			if jsonOutput:
				jsonResult['voltage'] = float(voltage) 
			if mqtt and split:
				if jsonOutput:
					mqttclient.publish(mqtttopic+"/voltage",json.dumps({ 'voltage': float(voltage) }))
				else:
					mqttclient.publish(mqtttopic+"/voltage",voltage)
	
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==54) or (register=="frequency"):
		frequency = '{0:.2f}'.format(readFloat(rs485,54))
		if frequency!='-1.00':
			alive = True
			if numeric:
				print(frequency)
			else:
				print('Frequency: {} Hz'.format(frequency))
			if jsonOutput:
				jsonResult['frequency'] = float(frequency) 
			if mqtt and split:
				if jsonOutput:
					mqttclient.publish(mqtttopic+"/frequency",json.dumps({ 'frequency': float(frequency) }))
				else:
					mqttclient.publish(mqtttopic+"/frequency",frequency)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==8) or (register=="current"):
		current = '{0:.2f}'.format(readFloat(rs485,8))
		if current!='-1.00':
			alive = True
			if numeric:
				print(current)
			else:
				print('Current: {} Amps'.format(current))
			if jsonOutput:
				jsonResult['current'] = float(current) 
			if mqtt and split:
				if jsonOutput:
					mqttclient.publish(mqtttopic+"/current",json.dumps({ 'current': float(current) }))
				else:
					mqttclient.publish(mqtttopic+"/current",current)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==18) or (register=="power"):
		power = '{0:.1f}'.format(readFloat(rs485,18))
		if power!='-1.0':
			alive = True
			if numeric:
				print(power)
			else:
				print('Active power: {} Watts'.format(power))
			if jsonOutput:
				jsonResult['power'] = float(power) 
			if mqtt and split:
				if jsonOutput:
					mqttclient.publish(mqtttopic+"/power",json.dumps({ 'active_power': float(power) }))
				else:
					mqttclient.publish(mqtttopic+"/power",power)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==42) or (register=="pf"):
		pf = '{0:.3f}'.format(readFloat(rs485,18))
		if pf!='-1.000':
			alive = True
			if numeric:
				print(pf)
			else:
				print('Power factor: {}'.format(pf))
			if jsonOutput:
				jsonResult['pf'] = float(pf) 
			if mqtt and split:
				if jsonOutput:
					mqttclient.publish(mqtttopic+"/pf",json.dumps({ 'pf': float(pf) }))
				else:
					mqttclient.publish(mqtttopic+"/pf",pf)

	# if jsonOutput:
	# 	if name:
	# 		jsonResult['name'] = name
		#jsonResult['err'] = int(alive == 'true')
	if mqtt:
		if alive:
			mqttclient.publish(mqtttopic+"/status","online")
			jsonResult['status'] = 'online'
		else:
			mqttclient.publish(mqtttopic+"/status","offline")
			jsonResult['status'] = 'offline'
		if not split:
			mqttclient.publish(mqtttopic,json.dumps(jsonResult))
		else:
			if jsonOutput:
				mqttclient.publish(mqtttopic+"/time",json.dumps({ 'time': jsonResult['time'] }))
				#mqttclient.publish(mqtttopic+"/err",json.dumps({ 'err': int(alive == 'true')}))
			else:
				mqttclient.publish(mqtttopic+"/time",jsonResult['time'])
				#mqttclient.publish(mqtttopic+"/err",int(alive == 'true'))
		if watchdog and alive:
			mqttclient.publish(mqtttopic+"/watchdog",0)

if __name__ == "__main__":
   main(sys.argv[1:])