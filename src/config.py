"""
Centraliza as configurações e constantes do Edge Node Monitor.
"""

# Definindo quais pinos do ESP32 vão usar cada sensor/LED
PIN_SENSOR_TEMP = 34      # Sensor NTC de temperatura
PIN_SENSOR_LOAD = 35      # Potenciômetro de carga
PIN_LED_COOLER = 2        # LED do cooler
PIN_LED_ALERT = 4         # LED de alerta

# Características do sensor NTC (termistor)
NTC_BETA = 3950           # Coeficiente BETA do termistor
NTC_ADC_RES = 4095        # Resolução do ADC (12 bits)

# Intervalo de leitura
READ_INTERVAL_MS = 1000   # Faz leitura a cada 1 segundo (sem travar o sistema)

# Limiares que disparam as ações
TEMP_COOLER_THRESHOLD = 50.0   # Ativa cooler acima de 50°C
TEMP_ALERT_THRESHOLD = 75.0    # Alerta crítico acima de 75°C
LOAD_ALERT_THRESHOLD = 90.0    # Alerta crítico acima de 90% de carga
