"""
O coração do sistema: monitora tudo que acontece no nó IoT.
Lê sensores, toma decisões, aciona LEDs. 
"""

import machine
import time
from config import (
    PIN_SENSOR_TEMP, PIN_SENSOR_LOAD, PIN_LED_COOLER, PIN_LED_ALERT,
    READ_INTERVAL_MS, TEMP_COOLER_THRESHOLD, TEMP_ALERT_THRESHOLD,
    LOAD_ALERT_THRESHOLD
)
from sensors import SensorNTC, SensorLoad


class EdgeNodeMonitor:
    """
    O monitor do nó de borda. Faz 3 coisas:
    1. Lê temperatura (sensor NTC) e carga (potenciômetro)
    2. Decide se deve ligar o cooler ou disparar alerta
    3. Printa relatório no console
    """
    
    def __init__(self):
        """Prepara tudo pra começar a monitorar."""
        # Coloca os sensores no lugar deles
        self.sensor_temp = SensorNTC(PIN_SENSOR_TEMP)
        self.sensor_load = SensorLoad(PIN_SENSOR_LOAD)
        
        # Prepara os LEDs pra acender quando precisar
        self.led_cooler = machine.Pin(PIN_LED_COOLER, machine.Pin.OUT)
        self.led_alert = machine.Pin(PIN_LED_ALERT, machine.Pin.OUT)
        
        # Rastreia o tempo pra fazer leitura a cada segundo (sem travar)
        self.last_read_time = time.ticks_ms()
        self.read_interval = READ_INTERVAL_MS

        self.buzzer = machine.Pin(13, machine.Pin.OUT)

    def read_sensors(self):
        """
        Lê os dois sensores e retorna os valores legáveis.
        
        Returns:
            tuple: (temperatura em °C, carga em %)
        """
        temp = self.sensor_temp.ler_temperatura_celsius()
        load = self.sensor_load.ler_carga_percentual()
        
        return temp, load

    def evaluate_logic(self, temp, load):
        """
        Analisa temperatura e carga, depois aciona os LEDs e o Buzzer.
        """
        # Se passou de 50°C, liga o ventilador
        cooler_active = temp > TEMP_COOLER_THRESHOLD
        self.led_cooler.value(1 if cooler_active else 0)
        
        # Se tá muito quente OU muito carregado, aciona alerta (LED + Buzzer)
        alert_active = temp > TEMP_ALERT_THRESHOLD or load > LOAD_ALERT_THRESHOLD
        
        # Atuadores de Alerta
        self.led_alert.value(1 if alert_active else 0)
        self.buzzer.value(1 if alert_active else 0)  
        
        return cooler_active, alert_active

    def _format_status(self, value):
        """Transforma True/False em ON/OFF pra ficar bonito."""
        return "ON" if value else "OFF"

    def _print_telemetry(self, cycle, cycles, temp, load, cooler, alert):
        """Exibe uma linha bonitinha com os dados de cada leitura."""
        cooler_status = self._format_status(cooler)
        alert_status = self._format_status(alert)
        
        msg = "[{}/{}] Temp: {:.1f}C | Load: {:.1f}% -> Cooler: {} | Alert: {}".format(
            cycle, cycles, temp, load, cooler_status, alert_status
        )
        print(msg)

    def run(self, cycles=5):
        """
        Faz quantas leituras você quiser (sem travar o sistema).
        Cada leitura toma uma decisão e exibe um relatório.
        
        Args:
            cycles: Quantas vezes ler (padrão: 5)
        """
        print("\n--- [EDGE NODE MONITOR] ---")
        cycle_count = 0
        
        while cycle_count < cycles:
            current_time = time.ticks_ms()
            
            # Só faz leitura se passou 1 segundo (sem usar sleep que trava)
            if time.ticks_diff(current_time, self.last_read_time) >= self.read_interval:
                self.last_read_time = current_time
                
                # Puxa os dados e toma a decisão
                temp, load = self.read_sensors()
                cooler, alert = self.evaluate_logic(temp, load)
                
                # Mostra o resultado
                self._print_telemetry(cycle_count + 1, cycles, temp, load, cooler, alert)
                
                cycle_count += 1
