import machine
import time
import sys

print("--- Inicializando Node Hardware ---")

# Mapeamento de Hardware
temp_sensor = machine.ADC(machine.Pin(34))
load_sensor = machine.ADC(machine.Pin(35))
led_cooler = machine.Pin(2, machine.Pin.OUT)
led_alerta = machine.Pin(4, machine.Pin.OUT)

time.sleep(1)

print("Hardware OK")
print('Type "help()" for more information.')
sys.exit(0)