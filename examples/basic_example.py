#!/usr/bin/env python3
"""
Ejemplo básico de uso del osciloscopio digital.
Captura y visualiza una señal simulada.
"""

from osciloscopio import DigitalOscilloscope, FilterType

def main():
    # Crea el osciloscopio con fuente simulada
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    
    # Inicia la captura
    osc.start()
    
    # Captura 2 segundos de datos
    print("\n--- CAPTURANDO SEÑAL ---")
    data = osc.capture(duration=2.0)
    
    # Analiza la señal
    print("\n--- ANÁLISIS DE SEÑAL ORIGINAL ---")
    osc.print_analysis(use_filtered=False)
    
    # Visualiza la señal original
    print("\n--- VISUALIZANDO SEÑAL ---")
    osc.plot_signal(use_filtered=False, save_path='signal_original.png')
    
    # Aplica un filtro paso bajo
    print("\n--- APLICANDO FILTRO ---")
    osc.apply_filter(FilterType.LOWPASS, cutoff=50.0, order=4)
    
    # Analiza la señal filtrada
    print("\n--- ANÁLISIS DE SEÑAL FILTRADA ---")
    osc.print_analysis(use_filtered=True)
    
    # Visualiza comparación
    print("\n--- COMPARANDO SEÑALES ---")
    osc.plot_comparison(save_path='signal_comparison.png')
    
    # Visualiza espectro de frecuencia
    print("\n--- ESPECTRO DE FRECUENCIA ---")
    osc.plot_fft(use_filtered=False, max_freq=100, save_path='signal_fft.png')
    
    # Crea dashboard completo
    print("\n--- CREANDO DASHBOARD ---")
    osc.create_dashboard(save_path='dashboard.png')
    
    # Exporta datos
    print("\n--- EXPORTANDO DATOS ---")
    osc.export_data('signal_data.csv', use_filtered=False)
    
    # Detiene la captura
    osc.stop()
    
    print("\n✓ Ejemplo completado exitosamente")

if __name__ == '__main__':
    main()
