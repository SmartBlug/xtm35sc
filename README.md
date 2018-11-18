# xtm35sc
Modbus/RS485 driver for xtm35sc energy meter with mqtt publishing option
# Usage
```
xtm35sc.py is a RS485/Modbus driver with mqtt publishing option
xtm35sc.py version v1.0 

Usage: xtm35sc.py address [-h] [-i register] [-r {voltage|frequency|current|power|pf}] [-d deviceport] [-m mqttaddress] [-p mqttport] [-t mqtttopic] [-n] [-v] 

address         : device address on RS485 bus.
-h,--help       : display this message.
-i,--id         : device register by id.
-r,--register   : device register by name. This could be "voltage","frequency","current","power" or "pf".
-d,--deviceport : deviceport. Default is /dev/ttyUSB0.
-m,--mqtt       : mqtt brocker address. This enable mqtt message.
-p,--port       : mqtt brocker port. Default is 1883
-t,--topic      : mqtt topic. Default is "xtm35sc/{ADDR}" and "{ADDR}" will be replaced by device address.
-n,--numeric    : display only numeric results.
-v,--verbose    : activate verbose mode.
```