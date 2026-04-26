"""
Todos os sensores do Edge Node Monitor vivem aqui.
Cada sensor é responsável por ler dados brutos e converter em valores úteis.
"""

import machine
import math
from config import NTC_BETA, NTC_ADC_RES


class SensorNTC:
    """
    Sensor de temperatura NTC (um termistor sensível ao calor).
    Lê resistência e usa Steinhart-Hart pra converter em graus Celsius.
    """
    
    def __init__(self, pin_num):
        """
        Prepara o sensor NTC no pino ADC escolhido.
        
        Args:
            pin_num: Qual pino ADC do ESP32 (ex: 34)
        """
        self.adc = machine.ADC(machine.Pin(pin_num))
        self.adc.atten(machine.ADC.ATTN_11DB)
        self.adc.width(machine.ADC.WIDTH_12BIT)
        
        self.BETA = NTC_BETA
        self.ADC_RES = NTC_ADC_RES

    def ler_temperatura_celsius(self):
        """
        Lê o termistor e converte pra Celsius (de verdade, sem erros de sinal).
        Retorna com 1 casa decimal de precisão.
        
        Returns:
            float: Temperatura em °C
        """
        val = self.adc.read()
        
        # Se chegou nos limites, ajusta pra não quebrar na fórmula
        if val >= self.ADC_RES:
            val = self.ADC_RES - 1
        if val <= 0:
            val = 1
        
        # Fórmula Steinhart-Hart 
        # Transforma o valor ADC em razão de resistência
        r_ratio = 1.0 / (self.ADC_RES / float(val) - 1.0)
        
        # Calcula o inverso da temperatura em Kelvin
        inv_t = (1.0 / 298.15) + (1.0 / self.BETA) * math.log(r_ratio)
        
        # Converte de Kelvin pra Celsius (subtrai 273.15)
        temp_kelvin = 1.0 / inv_t
        celsius = temp_kelvin - 273.15
        
        return round(celsius, 1)


class SensorLoad:
    """
    Sensor de carga do sistema (um simples potenciômetro).
    Diz o quanto o sistema tá "carregado" em percentual.
    """
    
    def __init__(self, pin_num):
        """
        Configura o pino pra ler o potenciômetro de carga.
        
        Args:
            pin_num: Qual pino ADC (ex: 35)
        """
        self.adc = machine.ADC(machine.Pin(pin_num))
        self.adc.atten(machine.ADC.ATTN_11DB)

    def ler_carga_percentual(self):
        """
        Lê o potenciômetro e converte em porcentagem de carga (0-100%).
        
        Returns:
            float: Quanto o sistema tá carregado em %
        """
        l_raw = self.adc.read()
        load = (l_raw / 4095.0) * 100.0
        return load
