#!/usr/bin/env python3
"""
Script de prueba para validar la funcionalidad del osciloscopio.
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usar backend no-interactivo para testing

from osciloscopio import (
    DigitalOscilloscope, 
    FilterType,
    SimulatedSource,
    SignalProcessor,
    SignalAnalyzer
)

def test_basic_functionality():
    """Prueba la funcionalidad básica del osciloscopio."""
    print("\n" + "="*70)
    print("TEST 1: Funcionalidad Básica")
    print("="*70)
    
    try:
        # Crear osciloscopio
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        print("✓ Osciloscopio creado exitosamente")
        
        # Iniciar y capturar
        osc.start()
        print("✓ Captura iniciada")
        
        data = osc.capture(duration=1.0)
        print(f"✓ Datos capturados: {len(data)} muestras")
        
        # Verificar que hay datos
        assert len(data) == 1000, "Número incorrecto de muestras"
        assert not np.all(data == 0), "Los datos están vacíos"
        print("✓ Datos válidos")
        
        # Análisis
        results = osc.analyze()
        print(f"✓ Análisis completado: {len(results)} métricas calculadas")
        
        # Verificar métricas clave
        assert 'frequency' in results, "Falta métrica de frecuencia"
        assert 'rms' in results, "Falta métrica RMS"
        assert results['frequency'] > 0, "Frecuencia inválida"
        print("✓ Métricas válidas")
        
        osc.stop()
        print("✓ Captura detenida")
        
        print("\n✅ TEST 1 PASADO: Funcionalidad básica OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_signal_types():
    """Prueba diferentes tipos de señales."""
    print("\n" + "="*70)
    print("TEST 2: Tipos de Señales")
    print("="*70)
    
    signal_types = ['sine', 'square', 'triangle', 'sawtooth', 'mixed']
    
    try:
        for sig_type in signal_types:
            osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
            osc.source.signal_type = sig_type
            osc.start()
            data = osc.capture(duration=0.5)
            
            assert len(data) > 0, f"No hay datos para {sig_type}"
            assert not np.all(data == 0), f"Datos vacíos para {sig_type}"
            
            print(f"✓ Señal {sig_type}: OK ({len(data)} muestras)")
            osc.stop()
        
        print("\n✅ TEST 2 PASADO: Todos los tipos de señales funcionan")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_filters():
    """Prueba los filtros."""
    print("\n" + "="*70)
    print("TEST 3: Filtros")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        osc.start()
        osc.capture(duration=1.0)
        
        # Prueba diferentes filtros
        filters = [
            (FilterType.LOWPASS, {'cutoff': 50.0}),
            (FilterType.HIGHPASS, {'cutoff': 5.0}),
            (FilterType.BANDPASS, {'lowcut': 10.0, 'highcut': 50.0}),
            (FilterType.MOVING_AVERAGE, {'window_size': 5}),
            (FilterType.MEDIAN, {'kernel_size': 5}),
        ]
        
        for filter_type, params in filters:
            filtered = osc.apply_filter(filter_type, **params)
            assert len(filtered) > 0, f"Filtro {filter_type.value} no produjo datos"
            print(f"✓ Filtro {filter_type.value}: OK")
        
        osc.stop()
        print("\n✅ TEST 3 PASADO: Todos los filtros funcionan")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis():
    """Prueba las funciones de análisis."""
    print("\n" + "="*70)
    print("TEST 4: Análisis de Señales")
    print("="*70)
    
    try:
        analyzer = SignalAnalyzer(sample_rate=1000.0)
        
        # Genera una señal conocida
        t = np.linspace(0, 1, 1000)
        signal = 2.5 * np.sin(2 * np.pi * 10 * t)  # 10 Hz, amplitud 2.5
        
        # Análisis
        results = analyzer.analyze(signal)
        
        # Verificaciones
        assert abs(results['frequency'] - 10.0) < 1.0, "Frecuencia incorrecta"
        print(f"✓ Frecuencia detectada: {results['frequency']:.2f} Hz (esperado: 10 Hz)")
        
        assert abs(results['mean']) < 0.1, "Media debería estar cerca de 0"
        print(f"✓ Media: {results['mean']:.4f} V")
        
        expected_rms = 2.5 / np.sqrt(2)  # RMS de sinusoidal
        assert abs(results['rms'] - expected_rms) < 0.5, "RMS incorrecto"
        print(f"✓ RMS: {results['rms']:.4f} V (esperado: {expected_rms:.4f} V)")
        
        assert abs(results['peak_to_peak'] - 5.0) < 0.5, "Pico-pico incorrecto"
        print(f"✓ Pico-pico: {results['peak_to_peak']:.4f} V (esperado: 5.0 V)")
        
        print("\n✅ TEST 4 PASADO: Análisis correcto")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization():
    """Prueba las funciones de visualización."""
    print("\n" + "="*70)
    print("TEST 5: Visualización")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        osc.start()
        osc.capture(duration=1.0)
        osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)
        
        # Prueba diferentes visualizaciones (sin mostrar)
        import matplotlib.pyplot as plt
        plt.ioff()  # Desactiva modo interactivo
        
        print("  Generando gráfico de señal...")
        osc.plot_signal(save_path='/tmp/test_signal.png')
        print("  ✓ Gráfico de señal OK")
        
        print("  Generando comparación...")
        osc.plot_comparison(save_path='/tmp/test_comparison.png')
        print("  ✓ Comparación OK")
        
        print("  Generando FFT...")
        osc.plot_fft(save_path='/tmp/test_fft.png')
        print("  ✓ FFT OK")
        
        print("  Generando dashboard...")
        osc.create_dashboard(save_path='/tmp/test_dashboard.png')
        print("  ✓ Dashboard OK")
        
        osc.stop()
        
        print("\n✅ TEST 5 PASADO: Todas las visualizaciones funcionan")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pwm_decoding():
    """Prueba la decodificación PWM."""
    print("\n" + "="*70)
    print("TEST 6: Decodificación PWM")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=10000.0, source_type='simulated')
        osc.source.signal_type = 'square'
        osc.source.frequency = 100.0
        osc.source.amplitude = 5.0
        
        osc.start()
        osc.capture(duration=0.2)
        
        pwm_info = osc.decode_pwm()
        
        assert 'duty_cycle' in pwm_info, "Falta duty_cycle"
        assert 'frequency' in pwm_info, "Falta frequency"
        assert pwm_info['frequency'] > 0, "Frecuencia inválida"
        
        print(f"✓ Ciclo de trabajo: {pwm_info['duty_cycle']:.2f}%")
        print(f"✓ Frecuencia: {pwm_info['frequency']:.2f} Hz")
        
        osc.stop()
        
        print("\n✅ TEST 6 PASADO: Decodificación PWM OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_export():
    """Prueba la exportación de datos."""
    print("\n" + "="*70)
    print("TEST 7: Exportación de Datos")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        osc.start()
        osc.capture(duration=0.5)
        
        output_file = '/tmp/test_export.csv'
        osc.export_data(output_file)
        
        # Verifica que el archivo existe
        import os
        assert os.path.exists(output_file), "Archivo no creado"
        print(f"✓ Archivo exportado: {output_file}")
        
        # Verifica el contenido
        with open(output_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 1, "Archivo vacío"
            print(f"✓ Archivo contiene {len(lines)} líneas")
        
        osc.stop()
        
        print("\n✅ TEST 7 PASADO: Exportación OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 7 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los tests."""
    print("="*70)
    print("SUITE DE PRUEBAS - OSCILOSCOPIO DIGITAL")
    print("="*70)
    
    tests = [
        test_basic_functionality,
        test_signal_types,
        test_filters,
        test_analysis,
        test_visualization,
        test_pwm_decoding,
        test_export,
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests pasados: {passed}/{total}")
    print(f"Tests fallidos: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON! 🎉")
        return 0
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        return 1

if __name__ == '__main__':
    sys.exit(main())
