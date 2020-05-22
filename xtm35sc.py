#!/usr/bin/python3

import sys, getopt
import minimalmodbus
import paho.mqtt.client as paho
import time

version = "v1.0"
help = "xtm35sc.py address [-h] [-i register] [-r {voltage|frequency|current|power|pf}] [-d deviceport] [-m mqttaddress] [-p mqttport] [-P mqtttopicprefix] [-t mqtttopic] [-n] [-v]"
def usage():
	#help = 'xtm35sc.py address -i <register> -r <[voltage,frequency,current,power,pf]> -d <device port> -m <mqtt addr> -p <mqtt port> -t <topic> -n -v'
	print("xtm35sc.py is a Modbus/RS485 driver for xtm35sc energy meter with mqtt publishing option")
	print("xtm35sc.py version",version,"\n")
	print("Usage:",help,"\n")
	print("address         : device address on RS485 bus.")
	print("-h,--help       : display this message.")
	print("-i,--id         : device register by id.")
	print("-r,--register   : device register by name. This could be \"voltage\",\"frequency\",\"current\",\"power\" or \"pf\".")
	print("-d,--deviceport : deviceport. Default is /dev/ttyUSB0.")
	print("-m,--mqtt       : mqtt brocker address. This enable mqtt message.")
	print("-p,--port       : mqtt brocker port. Default is 1883")
	print("-P,--prefix     : mqtt prefix topic. Default is \"\\xtm35sc\"")
	print("-t,--topic      : mqtt topic. Default is \"{PREFIX}/{ADDR}\" and \"{ADDR}\" will be replaced by device address.")
	print("-n,--numeric    : display only numeric results.")
	print("-v,--verbose    : activate verbose mode.\n")

def readFloat(rs485,addr):
	retry = 0;
	while (retry<5):
		retry += 1
		try:	
			return rs485.read_float(addr, functioncode=4, numberOfRegisters=2)
		except:
			print('retry',addr)
			time.sleep(0.5)
	print("Can't connect to device address",addr)
	return -1
	
def main(argv):

	deviceport = '/dev/ttyUSB0'
	numeric = False
	verbose = False
	mqtt = False
	mqttport = 1883
	mqtttopicprefix = "/xtm35sc"
	mqtttopic = "{PREFIX}/{ADDR}"
	registerid = -1
	register = ""
	
	if len(argv)==0:
		print(help)
		sys.exit(2)
	else:
		try:
			address = int(argv[0])
		except:
			print(help)
			sys.exit(2)
		
	try:
		opts, args = getopt.getopt(argv[1:],"hi:r:d:P:t:m:p:nv",["help","id=","register=","deviceport=","prefix=","topic=","mqtt=","port=","numeric","verbose"])
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
		elif opt in ("-v", "--verbose"):
			verbose = True
		elif opt in ("-d", "--deviceport"):
			deviceport = arg

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
			mqttclient = paho.Client("xtm35sc")
			mqttclient.connect(mqtt,mqttport)			
			mqtttopic = mqtttopic.replace("{PREFIX}",str(mqtttopicprefix))
			mqtttopic = mqtttopic.replace("{ADDR}",str(address))
		else:
			mqtttopic = False
	except:
		print("Can't connect to",mqtt,":",mqttport)

	alive = 0;
	if (registerid==-1) or (registerid==0) or (register=="voltage"):
		#Volts = rs485.read_float(0, functioncode=4, numberOfRegisters=2)
		Volts = readFloat(rs485,0)
		if Volts!=-1:
			alive = 1
			if numeric:
				print('{0:.1f}'.format(Volts))
			else:
				print('Voltage: {0:.1f} Volts'.format(Volts))
			if mqtt:
					mqttclient.publish(mqtttopic+"/voltage",'%.1f' % Volts)
	
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==54) or (register=="frequency"):
		#Frequency = rs485.read_float(54, functioncode=4, numberOfRegisters=2)
		Frequency = readFloat(rs485,54)
		if Frequency!=-1:
			alive = 1
			if numeric:
				print('{0:.2f}'.format(Frequency))
			else:
				print('Frequency: {0:.2f} Hz'.format(Frequency))
			if mqtt:
					mqttclient.publish(mqtttopic+"/frequency",'%.2f' % Frequency)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==8) or (register=="current"):
		#Current = rs485.read_float(8, functioncode=4, numberOfRegisters=2)
		Current = readFloat(rs485,8)
		if Current!=-1:
			alive = 1
			if numeric:
				print('{0:.2f}'.format(Current))
			else:
				print('Current: {0:.2f} Amps'.format(Current))
			if mqtt:
					mqttclient.publish(mqtttopic+"/current",'%.2f' % Current)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==18) or (register=="power"):
		#Active_Power = rs485.read_float(18, functioncode=4, numberOfRegisters=2)
		Active_Power = readFloat(rs485,18)
		if Active_Power!=-1:
			alive = 1
			if numeric:
				print('{0:.1f}'.format(Active_Power))
			else:
				print('Active power: {0:.1f} Watts'.format(Active_Power))
			if mqtt:
					mqttclient.publish(mqtttopic+"/power",'%.1f' % Active_Power)
			
	time.sleep(0.2)		
	if (registerid==-1) or (registerid==42) or (register=="pf"):
		#Power_Factor = rs485.read_float(42, functioncode=4, numberOfRegisters=2)
		Power_Factor = readFloat(rs485,18)
		if Power_Factor!=-1:
			alive = 1
			if numeric:
				print('{0:.3f}'.format(Power_Factor))
			else:
				print('Power factor: {0:.3f}'.format(Power_Factor))
			if mqtt:
					mqttclient.publish(mqtttopic+"/pf",'%.3f' % Power_Factor)

	if mqtt:
		mqttclient.publish(mqtttopic+"/alive",alive)

if __name__ == "__main__":
   main(sys.argv[1:])
