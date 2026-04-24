import machine
import time

print("--- Teeste de Pipeline CI/CD ---")

led = machine.Pin(2, machine.Pin.OUT)

for i in range(3):
    led.value(1)
    print(f"Ciclo {i+1}: LED LIGADO")
    time.sleep(1)
    
    led.value(0)
    print(f"Ciclo {i+1}: LED DESLIGADO")
    time.sleep(1)

print("--- Simulação concluída ---")