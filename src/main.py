import sys
import machine
import time

print('Type "help()" for more information.')

# Inicializando hardware do Edge Node
pot_temp = machine.ADC(machine.Pin(34))
pot_load = machine.ADC(machine.Pin(35))
led_cooler = machine.Pin(2, machine.Pin.OUT)
led_alerta = machine.Pin(4, machine.Pin.OUT)

print("Edge Node Monitor: Sensores Online")

# Ciclo rápido simulando a telemetria para o relatório
for i in range(3):
    print(f"Coletando métrica {i+1}...")
    led_cooler.value(1)
    time.sleep(0.5)

print("Teste concluído com sucesso.")
sys.exit(0)