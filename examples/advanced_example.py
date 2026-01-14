#!/usr/bin/env python3
"""
Ejemplo avanzado: Análisis de diferentes tipos de señales.
"""

from osciloscopio import DigitalOscilloscope, FilterType, SimulatedSource

def analyze_signal_type(signal_type: str, frequency: float):
    """Analiza un tipo específico de señal."""
    print(f"\n{'='*70}")
    print(f"ANALIZANDO SEÑAL: {signal_type.upper()} a {frequency} Hz")
    print('='*70)
    
    # Crea osciloscopio con fuente simulada
    osc = DigitalOscilloscope(sample_rate=2000.0, source_type='simulated')
    
    # Configura los parámetros de la señal
    osc.set_source_parameters(
        frequency=frequency,
        amplitude=3.0,
        noise_level=0.1
    )
    
    # Cambia el tipo de señal
    osc.source.signal_type = signal_type
    
    # Captura
    osc.start()
    osc.capture(duration=1.0)
    
    # Análisis
    osc.print_analysis(use_filtered=False)
    
    # Visualiza
    filename = f'signal_{signal_type}_{int(frequency)}hz.png'
    osc.plot_signal(save_path=filename)
    
    # FFT
    fft_filename = f'fft_{signal_type}_{int(frequency)}hz.png'
    osc.plot_fft(max_freq=200, save_path=fft_filename)
    
    osc.stop()

def compare_filters():
    """Compara diferentes tipos de filtros."""
    print(f"\n{'='*70}")
    print("COMPARACIÓN DE FILTROS")
    print('='*70)
    
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    osc.source.signal_type = 'mixed'
    osc.source.noise_level = 0.3
    
    osc.start()
    osc.capture(duration=2.0)
    
    # Prueba diferentes filtros
    filters = [
        (FilterType.LOWPASS, {'cutoff': 30.0}),
        (FilterType.HIGHPASS, {'cutoff': 5.0}),
        (FilterType.BANDPASS, {'lowcut': 8.0, 'highcut': 15.0}),
        (FilterType.MOVING_AVERAGE, {'window_size': 10}),
    ]
    
    for filter_type, params in filters:
        print(f"\n--- Filtro: {filter_type.value} ---")
        osc.apply_filter(filter_type, **params)
        results = osc.analyze(use_filtered=True)
        print(f"Frecuencia detectada: {results['frequency']:.2f} Hz")
        print(f"SNR: {results['snr']:.2f} dB")
    
    osc.stop()

def analyze_pwm_signal():
    """Analiza señales PWM."""
    print(f"\n{'='*70}")
    print("ANÁLISIS DE SEÑAL PWM")
    print('='*70)
    
    osc = DigitalOscilloscope(sample_rate=10000.0, source_type='simulated')
    osc.source.signal_type = 'square'
    osc.source.frequency = 1000.0  # 1 kHz PWM
    osc.source.amplitude = 5.0
    osc.source.noise_level = 0.05
    
    osc.start()
    osc.capture(duration=0.1)
    
    # Decodifica PWM
    pwm_info = osc.decode_pwm()
    
    # Visualiza
    osc.plot_signal(save_path='pwm_signal.png')
    
    osc.stop()

def main():
    print("="*70)
    print("EJEMPLOS AVANZADOS - OSCILOSCOPIO DIGITAL")
    print("="*70)
    
    # Analiza diferentes tipos de señales
    signal_types = [
        ('sine', 50.0),
        ('square', 25.0),
        ('triangle', 30.0),
        ('mixed', 10.0),
    ]
    
    for sig_type, freq in signal_types:
        analyze_signal_type(sig_type, freq)
    
    # Compara filtros
    compare_filters()
    
    # Analiza PWM
    analyze_pwm_signal()
    
    print("\n" + "="*70)
    print("✓ Todos los ejemplos completados exitosamente")
    print("="*70)

if __name__ == '__main__':
    main()
