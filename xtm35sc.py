#!/usr/bin/python3

import sys, getopt
import minimalmodbus
import paho.mqtt.client as paho
import time

def main(argv):

	help = 'xtm35sc.py address -i <register> -r <[voltage,frequency,current,power,pf]> -m <mqtt addr> -p <mqtt port> -t <topic> -n -d'
	registerid = -1
	numeric = False
	register = ""
	debug = False
	mqtt = False
	mqttport = 1883
	mqtttopic = "xtm35sc/{ADDR}"
	
	if len(argv)==0:
		print(help)
		sys.exit(2)
	else:
		address = int(argv[0])
		
	try:
		opts, args = getopt.getopt(argv[1:],"hi:r:t:m:p:nd",["iid=","rregister=","ttopic","mmqtt","pport","nnumeric","debug"])
	except getopt.GetoptError:
		print(help)
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print(help)
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
		elif opt in ("-t", "--topic"):
			mqtttopic = arg
		elif opt in ("-n", "--numeric"):
			numeric = True
		elif opt in ("-d", "--debug"):
			debug = True

	rs485 = minimalmodbus.Instrument('/dev/ttyUSB0', address)
	rs485.serial.baudrate = 9600
	rs485.serial.bytesize = 8
	rs485.serial.parity = 'E'
	rs485.serial.stopbits = 1
	rs485.serial.timeout = 0.5
	rs485.debug = debug
	rs485.mode = minimalmodbus.MODE_RTU

	try:
		if mqtt:
			mqttclient = paho.Client("xtm35sc")
			mqttclient.connect(mqtt,mqttport)
			mqtttopic = mqtttopic.replace("{ADDR}",str(address))
	except:
		print("Can't connect to",mqtt,":",mqttport)

	try:	
		if (registerid==-1) or (registerid==0) or (register=="voltage"):
			Volts = rs485.read_float(0, functioncode=4, numberOfRegisters=2)
			if numeric:
				print('{0:.1f}'.format(Volts))
			else:
				print('Voltage: {0:.1f} Volts'.format(Volts))
			if mqtt:
					mqttclient.publish(mqtttopic+"/voltage",'%.1f' % Volts)

		time.sleep(0.2)		
		if (registerid==-1) or (registerid==54) or (register=="frequency"):
			Frequency = rs485.read_float(54, functioncode=4, numberOfRegisters=2)
			if numeric:
				print('{0:.2f}'.format(Frequency))
			else:
				print('Frequency: {0:.2f} Hz'.format(Frequency))
			if mqtt:
					mqttclient.publish(mqtttopic+"/frequency",'%.2f' % Frequency)
				
		time.sleep(0.2)		
		if (registerid==-1) or (registerid==8) or (register=="current"):
			Current = rs485.read_float(8, functioncode=4, numberOfRegisters=2)
			if numeric:
				print('{0:.2f}'.format(Current))
			else:
				print('Current: {0:.2f} Amps'.format(Current))
			if mqtt:
					mqttclient.publish(mqtttopic+"/current",'%.2f' % Current)
				
		time.sleep(0.2)		
		if (registerid==-1) or (registerid==18) or (register=="power"):
			Active_Power = rs485.read_float(18, functioncode=4, numberOfRegisters=2)
			if numeric:
				print('{0:.1f}'.format(Active_Power))
			else:
				print('Active power: {0:.1f} Watts'.format(Active_Power))
			if mqtt:
					mqttclient.publish(mqtttopic+"/power",'%.1f' % Active_Power)
				
		time.sleep(0.2)		
		if (registerid==-1) or (registerid==42) or (register=="pf"):
			Power_Factor = rs485.read_float(42, functioncode=4, numberOfRegisters=2)
			if numeric:
				print('{0:.3f}'.format(Power_Factor))
			else:
				print('Power factor: {0:.3f}'.format(Power_Factor))
			if mqtt:
					mqttclient.publish(mqtttopic+"/pf",'%.3f' % Power_Factor)

		if mqtt:
			mqttclient.publish(mqtttopic+"/alive","1")

	except:
		if numeric:
			print(-1)
		else:
			print("Can't connect to device",address)
		if mqtt:
			mqttclient.publish(mqtttopic+"/alive","0")
			
if __name__ == "__main__":
   main(sys.argv[1:])
