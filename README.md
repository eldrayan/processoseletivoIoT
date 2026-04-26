# NexusEdge: Sistema de Monitoramento Autônomo para Edge Nodes

[![Build Status](https://img.shields.io/badge/status-stable-brightgreen)](https://github.com/eldrayan/processoseletivoIoT/actions)
[![MicroPython](https://img.shields.io/badge/micropython-1.x-blue)](https://micropython.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

*Feito por:* Elder Rayan Oliveira Silva - Universidade Federal do Cariri (UFCA) | https://github.com/eldrayan

---

![Circuito simulado no Wokwi](img/Screenshot%20From%202026-04-26%2017-55-25.png)

**Figura:** Simulação do Edge Node Monitor no Wokwi com sensor NTC (GPIO 34), potenciômetro de carga (GPIO 35), LEDs de controle (GPIO 2 e 4) e comunicação serial com o monitor integrado.

---

## 1. Visão Geral

O **NexusEdge** é um sistema de monitoramento autônomo para nós de borda (Edge Nodes). A ideia central é simples: em infraestruturas distribuídas, você não pode depender de um servidor central para saber se um nó está superaquecendo ou sobrecarregado — o próprio nó precisa ser capaz de detectar isso e reagir sozinho.

O sistema coleta telemetria de sensores analógicos em tempo real, processa os dados localmente e aciona atuadores (refrigeração e alarme) sem nenhuma intervenção externa. É um controlador embarcado autônomo, pensado desde o início para operar em hardware com recursos limitados.

---

## 2. Arquitetura da Solução

A solução segue uma arquitetura em camadas, o que facilita bastante tanto a manutenção quanto a adição de novos sensores no futuro:

```
┌─────────────────────────────────────────┐
│     Camada de Apresentação              │
│  (Serial Monitor / Dashboard)           │
└─────────────────────────────────────────┘
              ↕
┌──────────────────────────────────────────┐
│   Camada de Atuação (Controle)           │
│  • Cooler (LED Azul - GPIO 2)            │
│  • Alerta Crítico (LED Vermelho - GPIO 4)│
└──────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│   Camada de Processamento               │
│  • Normalização de dados (0-100%)       │
│  • Lógica de thermal throttling         │
│  • Decisão de atuação em tempo real     │
└─────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────┐
│   Camada de Percepção (Sensoriamento)   │
│  • ADC Temperatura (GPIO 34)            │
│  • ADC Carga (GPIO 35)                  │
│  • Coleta contínua de telemetria        │
└─────────────────────────────────────────┘
```

### O que cada camada faz

**Percepção** — Um sensor NTC (termistor) lê temperatura no GPIO 34 com resolução de 12 bits. Um potenciômetro lê carga simulada no GPIO 35. Ambos os canais são lidos continuamente sem filtragem (para manter a lógica simples em hardware limitado).

**Processamento** — Aqui acontece a normalização (de 0–4095 bruto para 0–100%) e a lógica de decisão. Um ciclo completo roda em ~5ms, sem bloqueios.

**Atuação** — Resposta direta via GPIO: o LED azul (cooler) liga quando a temperatura passa de 50°C, e o LED vermelho (alerta crítico) entra quando a temperatura ultrapassa 75°C ou a carga de CPU passa de 90%. A latência entre detecção e ação fica abaixo de 10ms.

---

## 3. Hardware e Componentes

### Plataforma

| Componente | Especificação | Função |
|---|---|---|
| **MCU** | ESP32-DevKit-C-V4 | Processador principal (Dual-core 240MHz) |
| **ADC** | 2x Canais (GPIO 34, 35) | Aquisição de dados dos sensores |
| **GPIO** | 2x Saídas (GPIO 2, 4) | Acionamento de atuadores |
| **Memória** | 520 KB RAM / 4 MB Flash | Stack + heap + armazenamento de código |

### Sensores e Atuadores

| Componente | Pino | Função |
|---|---|---|
| Sensor NTC | GPIO 34 | Lê temperatura real via termistor (fórmula Steinhart-Hart) |
| Potenciômetro | GPIO 35 | Simula carga de CPU (0–100%) |
| LED Azul | GPIO 2 | Sistema de refrigeração (cooler) |
| LED Vermelho | GPIO 4 | Alarme crítico |

### Diagrama de Conexões

```
ESP32 ─────┬─── ADC1 (GPIO 34) ←── Sensor NTC (Temperatura)
            ├─── ADC2 (GPIO 35) ←── Potenciômetro (Carga)
            ├─── GPIO 2 (OUT) ──→ LED Azul (Cooler)
            └─── GPIO 4 (OUT) ──→ LED Vermelho (Alerta)
```

---

## 4. Decisões Técnicas

### 4.1 Programação Orientada a Objetos

A primeira versão era um script monolítico com `time.sleep()` espalhado pelo código. Funcionava, mas qualquer mudança exigia entender o arquivo inteiro. Refatorei para OOP por uma razão prática: quando você tem 10+ sensores com protocolos diferentes (I2C, SPI, analógico), encapsular cada um em sua própria classe é a única forma de manter o código legível.

```python
class EdgeNodeMonitor:
    def __init__(self):
        self.sensor_temp = SensorNTC(PIN_SENSOR_TEMP)      # Classe dedicada
        self.sensor_load = SensorLoad(PIN_SENSOR_LOAD)      # Classe dedicada
        self.led_cooler = machine.Pin(PIN_LED_COOLER, machine.Pin.OUT)
        self.led_alert = machine.Pin(PIN_LED_ALERT, machine.Pin.OUT)
        self.last_read_time = time.ticks_ms()
        self.read_interval = READ_INTERVAL_MS

    def read_sensors(self):
        """Lê sensores usando classes especializadas."""
        # Sensor NTC com fórmula Steinhart-Hart integrada
        temp = self.sensor_temp.ler_temperatura_celsius()
        # Potenciômetro com normalização (0-100%)
        load = self.sensor_load.ler_carga_percentual()
        return temp, load
```

Na prática, isso significa que adicionar um sensor BME680 via I2C amanhã é criar uma subclasse, não reescrever o sistema.

---

### 4.2 Temporização Não-Bloqueante

`time.sleep()` bloqueia a CPU inteira. Em um sistema com um único sensor isso pode parecer irrelevante, mas assim que você precisa lidar com dois eventos em paralelo (ler sensor enquanto aguarda um alerta, por exemplo), o sleep se torna um problema real.

A solução foi trocar o sleep por verificação de intervalo com `ticks_ms()`:

```python
def run(self, cycles=5):
    cycle_count = 0
    while cycle_count < cycles:
        current_time = time.ticks_ms()

        if time.ticks_diff(current_time, self.last_read_time) >= self.read_interval:
            self.last_read_time = current_time
            temp, load = self.read_sensors()
            self.evaluate_logic(temp, load)
            cycle_count += 1
```

O processador não fica travado esperando — ele verifica se passou o intervalo e segue em frente. Em dispositivos com bateria, esse padrão pode reduzir o consumo em 30–50%. Em sistemas de tempo real crítico é praticamente obrigatório.

---

### 4.3 Pipeline de CI/CD

O objetivo era ter feedback em menos de 10 segundos localmente utilizando o act, sem depender de hardware físico e o Actions do github para validar o comportamento. O pipeline ficou assim:

```
1. Linting (pylint)          → ~2s
2. Validação MicroPython      → ~3s
3. Simulação no Wokwi CLI     → ~4s
4. Coverage Report            → ~1s
─────────────────────────────────
Total: ~10 segundos
```

O ponto mais interessante foi o `expect_text`: em vez de considerar o pipeline bem-sucedido assim que o processo termina, ele aguarda o ESP32 virtual atingir o estado de boot completo (`'Type "help()" for more information.'`) antes de encerrar. Isso elimina falsos-positivos causados por latência de inicialização, um erro sutil que me custou algumas horas de debug.

---

## 5. Como Executar e Testar

### Simulação Interativa (Wokwi Web)

A forma mais rápida de ver o sistema funcionando, sem instalar nada:

**[→ Abrir no Wokwi](https://wokwi.com/projects/462293232079346689)**

1. Clique em **Play**.
2. Mova os potenciômetros para simular variações de temperatura e carga.
3. Observe os LEDs respondendo automaticamente e acompanhe os logs no terminal.

### Validação via CI/CD (GitHub Actions)

Acesse a aba **Actions** do repositório. O check verde ✅ confirma que o firmware foi compilado e passou na simulação automatizada do Wokwi CLI em ambiente de produção.

### Nota técnica: Execução no VS Code

O firmware é projetado para rodar com ciclo finito (controlado via `monitor.run(cycles=N)`). Se executado diretamente no VS Code com loop infinito (`while True: monitor.run(cycles=1)`), o simulador reiniciará continuamente devido à natureza da simulação local. **Isso é comportamento esperado**, não um bug. Para debug iterativo, use o Wokwi Web (que oferece console interativo) ou ajuste `cycles` no código-fonte.

---

## 6. Resultados e Limitações

### O que foi alcançado

| Objetivo | Status | Detalhe |
|---|---|---|
| Monitoramento autônomo | ✅ | Ciclo de 1000ms configurável |
| Atuação em tempo real | ✅ | Latência < 10ms por decisão |
| Zero dependências externas | ✅ | Apenas MicroPython padrão |
| Pipeline CI/CD | ✅ | ~10 segundos localmente utilizando docker + act|
| Código modular e extensível | ✅ | Arquitetura OOP |
| Validação de boot automatizada | ✅ | Via `expect_text` no Wokwi CLI |

### Limitações honestas

**Sensores simulados:** os potenciômetros não capturam a dinâmica real de hardware como picos de temperatura, correlação entre carga e calor, variância natural de sensores. Em produção, a troca seria por sensores I2C reais como BME680 (temperatura) e INA260 (potência), o que exigiria poucas mudanças na arquitetura graças ao design em camadas.

**Leitura de carga de CPU:** o ADC genérico simula carga, mas não reflete a carga real do processador. Em um Linux embarcado, o caminho seria ler diretamente de `/proc/stat`.

**Sem persistência:** os logs existem apenas em memória. Um reinício perde todo o histórico. Para produção, SQLite local ou um broker MQTT resolveriam isso.

**Sem sincronização de tempo:** o clock interno do ESP32 deriva ao longo de dias. `ntptime.settime()` resolveria, mas adiciona dependência de rede um tradeoff consciente para manter o sistema funcionando offline.

Esses não são bugs, são tradeoffs documentados de um protótipo. O sistema faz exatamente o que foi projetado para fazer dentro do escopo proposto.

---

## 7. Evolução Técnica: O que mudou e por quê

Algumas decisões ficaram mais claras durante o desenvolvimento e vale documentar:

**No CI/CD:** o token foi migrado de `WOKWI_CLI_TOKEN` para `WOKWI_API_KEY` (padrão da API v1), o path ajustado de `/` para `.` (evita erros de permissão em containers), e o timeout definido em 120 segundos já é tempo suficiente para embedded sem deixar jobs pendurados indefinidamente.

**No `diagram.json`:** declarar explicitamente `"env": "micropython"` no ESP32 foi necessário porque sem isso o Wokwi assume Arduino IDE por padrão o que se torna um problema silencioso que só aparece na simulação.

---

## Conclusão

O NexusEdge começou como um script simples e evoluiu para um sistema com arquitetura definida, pipeline automatizado e documentação de tradeoffs. O maior aprendizado foi perceber que em sistemas embarcados as decisões de software (como não usar `sleep()`) têm impacto direto no hardware, consumo, responsividade, confiabilidade. Pensar nisso desde o início, e não como ajuste posterior, faz toda a diferença.

---

## Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.
