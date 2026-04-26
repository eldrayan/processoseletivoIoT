"""
Arquivo principal que centraliza e coloca tudo para rodar.
"""

from monitor import EdgeNodeMonitor


def main():
    """Inicia o monitor"""
    try:
        monitor = EdgeNodeMonitor()
        
        # Roda infinitamente, fazendo uma leitura por vez
        # (mantém tudo responsivo, sem travar)
        while True:
            monitor.run(cycles=1)
            
    except KeyboardInterrupt:
        print("\n\n[SISTEMA] Monitor desligado")
    except Exception as e:
        print("[ERRO] Falha crítica no hardware: {}".format(e))


if __name__ == "__main__":
    main()