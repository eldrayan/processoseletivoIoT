import sys
print('Type "help()" for more information.')

import machine

temp_sensor = machine.ADC(machine.Pin(34))
load_sensor = machine.ADC(machine.Pin(35))
led_cooler = machine.Pin(2, machine.Pin.OUT)
led_alerta = machine.Pin(4, machine.Pin.OUT)

print("Hardware Initialized")
sys.exit(0)