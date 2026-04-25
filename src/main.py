import sys
import machine
import time

class EdgeNodeMonitor:
    """
    Classe responsável por simular um nó de borda IoT.
    Métricas de telemetria coletadas: Temperatura da CPU e Carga de Sistema.
    """
    
    def __init__(self):
        # Mapeamento e Configuração de Pinos
        self.adc_temp = machine.ADC(machine.Pin(34))
        self.adc_temp.atten(machine.ADC.ATTN_11DB) # Permite leitura de 0-3.3V
        
        self.adc_load = machine.ADC(machine.Pin(35))
        self.adc_load.atten(machine.ADC.ATTN_11DB)
        
        self.led_cooler = machine.Pin(2, machine.Pin.OUT)
        self.led_alert = machine.Pin(4, machine.Pin.OUT)
        
        # Variáveis de controle de tempo 
        self.last_read_time = time.ticks_ms()
        self.read_interval = 1000 # (1000 ms)

    def read_sensors(self):
        """Lê os sensores e converte os valores brutos para métricas percentuais."""
        t_raw = self.adc_temp.read()
        l_raw = self.adc_load.read()
        
        # Normalização (0-100%)
        temp = (t_raw / 4095.0) * 100.0
        load = (l_raw / 4095.0) * 100.0
        
        return temp, load

    def evaluate_logic(self, temp, load):
        """Aplica as regras de negócio baseadas nas métricas."""
        # Regra 1: Aciona cooler se Temp > 50C
        cooler_active = temp > 50.0
        self.led_cooler.value(1 if cooler_active else 0)
        
        # Regra 2: Alerta Crítico se Temp > 80C OU Load > 90%
        alert_active = temp > 80.0 or load > 90.0
        self.led_alert.value(1 if alert_active else 0)
        
        return cooler_active, alert_active

    def run(self, cycles=5):
        """Executa a máquina de estados principal."""
        print("\n--- [EDGE NODE MONITOR INIT] ---")
        cycle_count = 0
        
        # Loop Principal com Temporização Não-Bloqueante
        while cycle_count < cycles:
            current_time = time.ticks_ms()
            
            # Verifica se já passou o intervalo de leitura
            if time.ticks_diff(current_time, self.last_read_time) >= self.read_interval:
                self.last_read_time = current_time 
                
                temp, load = self.read_sensors()
                cooler, alert = self.evaluate_logic(temp, load)
                
                # Relatório no console (Logs de Sistema)
                status_cooler = "ON" if cooler else "OFF"
                status_alert = "ON" if alert else "OFF"
                
                print(f"[{cycle_count+1}/{cycles}] Temp: {temp:.1f}C | Load: {load:.1f}% -> Cooler: {status_cooler} | Alert: {status_alert}")
                
                cycle_count += 1

# === Execução do Programa ===
if __name__ == "__main__":
    try:
        # Instancia e roda a simulação por 5 ciclos (para o CI passar rápido)
        monitor = EdgeNodeMonitor()
        monitor.run(cycles=5)
        print("\nSimulação concluída com sucesso.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal de hardware: {e}")