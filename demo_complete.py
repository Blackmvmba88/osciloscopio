#!/usr/bin/env python3
"""
Demo completo del Sistema de Osciloscopio Digital.
Muestra todas las capacidades del sistema.
"""

import sys
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo

from osciloscopio import DigitalOscilloscope, FilterType

def print_header(title):
    """Imprime un encabezado formateado."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def demo_signal_capture():
    """Demuestra captura básica de señales."""
    print_header("1. CAPTURA DE SEÑALES SIMULADAS")
    
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    
    # Configurar señal
    osc.set_source_parameters(
        frequency=25.0,
        amplitude=3.5,
        noise_level=0.15
    )
    
    print("\n✓ Configuración:")
    print(f"  - Frecuencia: 25 Hz")
    print(f"  - Amplitud: 3.5 V")
    print(f"  - Nivel de ruido: 0.15 V")
    
    # Capturar
    osc.start()
    data = osc.capture(duration=2.0)
    
    print(f"\n✓ Captura completada: {len(data)} muestras")
    
    # Análisis rápido
    results = osc.analyze()
    print(f"\n✓ Análisis rápido:")
    print(f"  - Frecuencia detectada: {results['frequency']:.2f} Hz")
    print(f"  - Valor RMS: {results['rms']:.3f} V")
    print(f"  - Pico-pico: {results['peak_to_peak']:.3f} V")
    
    osc.stop()
    return osc

def demo_filters():
    """Demuestra diferentes filtros."""
    print_header("2. FILTROS CONFIGURABLES")
    
    osc = DigitalOscilloscope(sample_rate=2000.0, source_type='simulated')
    osc.source.signal_type = 'mixed'
    osc.source.noise_level = 0.5
    
    print("\n✓ Señal compleja con múltiples armónicos y ruido")
    
    osc.start()
    osc.capture(duration=1.5)
    
    original_snr = osc.analyze()['snr']
    print(f"\n  SNR original: {original_snr:.2f} dB")
    
    # Aplicar filtro paso bajo
    osc.apply_filter(FilterType.LOWPASS, cutoff=30.0)
    filtered_snr = osc.analyze(use_filtered=True)['snr']
    
    print(f"  SNR filtrado: {filtered_snr:.2f} dB")
    print(f"  Mejora: {filtered_snr - original_snr:.2f} dB ✓")
    
    osc.stop()
    return osc

def demo_signal_types():
    """Demuestra diferentes tipos de señales."""
    print_header("3. TIPOS DE SEÑALES SOPORTADAS")
    
    signal_types = {
        'sine': 'Onda Sinusoidal',
        'square': 'Onda Cuadrada',
        'triangle': 'Onda Triangular',
        'sawtooth': 'Diente de Sierra',
        'mixed': 'Señal Compleja'
    }
    
    for sig_type, description in signal_types.items():
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        osc.source.signal_type = sig_type
        osc.source.frequency = 20.0
        
        osc.start()
        osc.capture(duration=0.5)
        results = osc.analyze()
        
        print(f"\n  {description} ({sig_type}):")
        print(f"    Frecuencia: {results['frequency']:.2f} Hz")
        print(f"    RMS: {results['rms']:.3f} V")
        
        osc.stop()

def demo_pwm_decode():
    """Demuestra decodificación PWM."""
    print_header("4. DECODIFICACIÓN PWM")
    
    # Simula señal PWM
    osc = DigitalOscilloscope(sample_rate=20000.0, source_type='simulated')
    osc.source.signal_type = 'square'
    osc.source.frequency = 500.0  # 500 Hz PWM
    osc.source.amplitude = 5.0
    
    print("\n✓ Señal PWM simulada:")
    print(f"  - Frecuencia: 500 Hz")
    print(f"  - Amplitud: 5.0 V")
    
    osc.start()
    osc.capture(duration=0.1)
    
    pwm_info = osc.decode_pwm()
    
    print(f"\n✓ Información decodificada:")
    print(f"  - Ciclo de trabajo: {pwm_info['duty_cycle']:.2f}%")
    print(f"  - Frecuencia PWM: {pwm_info['frequency']:.2f} Hz")
    print(f"  - Período: {pwm_info['period']*1000:.3f} ms")
    
    osc.stop()

def demo_analysis():
    """Demuestra análisis completo."""
    print_header("5. ANÁLISIS COMPLETO DE SEÑAL")
    
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    osc.source.frequency = 15.0
    osc.source.amplitude = 2.8
    
    osc.start()
    osc.capture(duration=2.0)
    
    print("\n✓ Métricas calculadas:")
    osc.print_analysis()
    
    osc.stop()

def demo_visualization():
    """Demuestra capacidades de visualización."""
    print_header("6. VISUALIZACIÓN INTERACTIVA")
    
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    osc.source.signal_type = 'mixed'
    osc.source.frequency = 20.0
    
    osc.start()
    osc.capture(duration=1.5)
    osc.apply_filter(FilterType.LOWPASS, cutoff=60.0)
    
    print("\n✓ Generando visualizaciones...")
    
    # Señal en tiempo
    osc.plot_signal(save_path='demo_signal.png')
    print("  - Señal en tiempo: demo_signal.png")
    
    # Comparación
    osc.plot_comparison(save_path='demo_comparison.png')
    print("  - Comparación: demo_comparison.png")
    
    # FFT
    osc.plot_fft(max_freq=150, save_path='demo_fft.png')
    print("  - Espectro FFT: demo_fft.png")
    
    # Dashboard
    osc.create_dashboard(save_path='demo_dashboard.png')
    print("  - Dashboard completo: demo_dashboard.png")
    
    osc.stop()

def demo_export():
    """Demuestra exportación de datos."""
    print_header("7. EXPORTACIÓN DE DATOS")
    
    osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
    
    osc.start()
    osc.capture(duration=1.0)
    
    # Exportar datos crudos
    osc.export_data('demo_raw_data.csv', use_filtered=False)
    print("\n✓ Datos crudos exportados: demo_raw_data.csv")
    
    # Aplicar filtro y exportar
    osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)
    osc.export_data('demo_filtered_data.csv', use_filtered=True)
    print("✓ Datos filtrados exportados: demo_filtered_data.csv")
    
    osc.stop()

def demo_hardware_ready():
    """Demuestra capacidad de conexión con hardware."""
    print_header("8. COMPATIBILIDAD CON HARDWARE")
    
    print("\n✓ El sistema soporta hardware externo vía puerto serial")
    print("\n  Configuración típica:")
    print("  --------------------------------------------------")
    print("  osc = DigitalOscilloscope(")
    print("      sample_rate=1000.0,")
    print("      source_type='hardware'")
    print("  )")
    print("  osc.source.port = '/dev/ttyUSB0'  # Linux")
    print("  # osc.source.port = 'COM3'         # Windows")
    print("  osc.source.baudrate = 115200")
    print("  --------------------------------------------------")
    print("\n✓ Si no hay hardware, automáticamente usa simulación")
    print("✓ Formato de datos: Un valor flotante por línea")

def main():
    """Ejecuta todas las demos."""
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*15 + "OSCILOSCOPIO DIGITAL - DEMO COMPLETA" + " "*17 + "║")
    print("║" + " "*10 + "Sistema de Captura y Análisis de Señales" + " "*18 + "║")
    print("╚" + "═"*68 + "╝")
    
    try:
        demo_signal_capture()
        demo_filters()
        demo_signal_types()
        demo_pwm_decode()
        demo_analysis()
        demo_visualization()
        demo_export()
        demo_hardware_ready()
        
        print("\n")
        print("╔" + "═"*68 + "╗")
        print("║" + " "*20 + "🎉 DEMO COMPLETADA EXITOSAMENTE 🎉" + " "*15 + "║")
        print("╚" + "═"*68 + "╝")
        print("\nCaracterísticas demostradas:")
        print("  ✓ Captura de señales (simuladas y hardware)")
        print("  ✓ Múltiples tipos de señales")
        print("  ✓ Filtros configurables")
        print("  ✓ Análisis completo (13+ métricas)")
        print("  ✓ Decodificación PWM")
        print("  ✓ Visualización interactiva")
        print("  ✓ Exportación de datos")
        print("  ✓ Modular y extensible")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error en la demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
