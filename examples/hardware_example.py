#!/usr/bin/env python3
"""
Ejemplo de uso con hardware externo.
Configura el osciloscopio para leer desde un puerto serial.
"""

from osciloscopio import DigitalOscilloscope, FilterType

def main():
    print("="*70)
    print("OSCILOSCOPIO DIGITAL - MODO HARDWARE")
    print("="*70)
    
    # Intenta conectar con hardware
    # Si falla, automáticamente usa modo simulación
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='hardware')
    
    # Configura el puerto (opcional, tiene valores por defecto)
    if hasattr(osc.source, 'port'):
        osc.source.port = '/dev/ttyUSB0'  # Linux
        # osc.source.port = 'COM3'  # Windows
        osc.source.baudrate = 115200
    
    # Inicia la captura
    osc.start()
    
    # Captura datos
    print("\n--- CAPTURANDO DESDE HARDWARE ---")
    osc.capture(duration=5.0)
    
    # Analiza
    print("\n--- ANÁLISIS ---")
    osc.print_analysis()
    
    # Aplica filtro para limpiar ruido
    print("\n--- APLICANDO FILTRO PASO BAJO ---")
    osc.apply_filter(FilterType.LOWPASS, cutoff=100.0)
    
    # Visualiza
    print("\n--- GENERANDO VISUALIZACIONES ---")
    osc.plot_comparison(save_path='hardware_comparison.png')
    osc.plot_fft(save_path='hardware_fft.png')
    
    # Exporta datos
    osc.export_data('hardware_data.csv')
    
    osc.stop()
    
    print("\n✓ Captura de hardware completada")

if __name__ == '__main__':
    main()
