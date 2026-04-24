import machine
import time
import sys

# Configuração de Pinos
LED_BOMBA = machine.Pin(2, machine.Pin.OUT) 
SENSOR_PIN = 34 
sensor = machine.ADC(machine.Pin(SENSOR_PIN))
sensor.atten(machine.ADC.ATTN_11DB)

def monitorar():
    print("--- Sistema Ativo ---")
    
    for i in range(2):
        valor = sensor.read()
        status = "SECO" if valor > 2000 else "UMIDO"
        
        print(f"Leitura {i+1}: Valor={valor} | Status={status}")
        
        if status == "SECO":
            LED_BOMBA.value(1)
            print("Ação: Ligando Bomba d'água...")
        else:
            LED_BOMBA.value(0)
            print("Ação: Solo hidratado. Bomba desligada.")
            
        time.sleep(0.5)

    print("--- Teste de Rotina Concluído ---")
    sys.exit(0) 

monitorar()