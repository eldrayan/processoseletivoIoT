import sys
print("MicroPython iniciado - Sistema OK")

import machine
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)

sys.exit(0)