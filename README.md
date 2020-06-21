# xtm35sc
Modbus/RS485 driver for xtm35sc energy meter with mqtt publishing option
# Usage
```
xtm35sc.py address [-h] [-i register] [-r {voltage|frequency|current|power|pf}] [-d deviceport] [-m mqttaddress] [-p mqttport] [-P mqtttopicprefix] [-t mqtttopic] [-j] [-s] [-n] [-v] [-N name] [-w]
xtm35sc.py is a Modbus/RS485 driver for xtm35sc energy meter with mqtt publishing option
xtm35sc.py version v1.2 

Usage: xtm35sc.py address [-h] [-i register] [-r {voltage|frequency|current|power|pf}] [-d deviceport] [-m mqttaddress] [-p mqttport] [-P mqtttopicprefix] [-t mqtttopic] [-j] [-s] [-n] [-v] [-N name] [-w] 

address         : device address on RS485 bus.
-h,--help       : display this message.
-i,--id         : device register by id.
-j,--json       : display results in json format. Default
-s,--split      : split result in sub topics.
-r,--register   : device register by name. This could be "voltage","frequency","current","power" or "pf".
-d,--deviceport : deviceport. Default is /dev/ttyUSB0.
-m,--mqtt       : mqtt brocker address. This enable mqtt message.
-p,--port       : mqtt brocker port. Default is 1883
-P,--prefix     : mqtt prefix topic. Default is "xtm35sc"
-t,--topic      : mqtt topic. Default is "{PREFIX}/{ADDR}" and "{ADDR}" will be replaced by device address or name if -N.
-n,--numeric    : display only numeric results. This disable json output
-N,--name       : add name tag to json
-v,--verbose    : activate verbose mode.
-w,--watchdog   : reset watchdog on topic "{PREFIX}/{ADDR}/watchdog".
```
ex:
```
./xtm35sc.py 47
```
return
```
Voltage: 232.7 Volts
Frequency: 50.00 Hz
Current: 0.60 Amps
Active power: 75.5 Watts
Power factor: 75.530
```