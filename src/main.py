import machine
import time
import sys

print("--- Iniciando Simulação ---")
led = machine.Pin(2, machine.Pin.OUT)

for i in range(3):
    led.value(1)
    print("LED ON")
    time.sleep(0.2)
    
    led.value(0)
    print("LED OFF")
    time.sleep(0.2)

print("--- Sucesso! Encerrando antes do Timeout ---")
sys.exit(0) 