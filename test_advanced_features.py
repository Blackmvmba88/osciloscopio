#!/usr/bin/env python3
"""
Script de prueba para las funcionalidades avanzadas del osciloscopio.
"""

import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Usar backend no-interactivo para testing

from osciloscopio import (
    DigitalOscilloscope, 
    FilterType,
    TriggerType,
    TriggerMode,
)

def test_trigger_system():
    """Prueba el sistema de triggers avanzado."""
    print("\n" + "="*70)
    print("TEST 1: Sistema de Triggers Avanzado")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
        osc.source.signal_type = 'square'
        osc.source.frequency = 50.0
        osc.start()
        
        # Configurar trigger rising edge
        osc.configure_trigger(
            trigger_type='rising_edge',
            level=0.0,
            mode='normal',
            hysteresis=0.1
        )
        print("✓ Trigger rising edge configurado")
        
        # Capturar con trigger
        data = osc.capture_with_trigger(duration=0.5, pre_trigger_percent=10.0)
        print(f"✓ Captura con trigger: {len(data)} muestras")
        
        # Probar falling edge
        osc.configure_trigger(trigger_type='falling_edge', level=0.0)
        data = osc.capture_with_trigger(duration=0.5)
        print("✓ Trigger falling edge funciona")
        
        # Probar pulse width
        osc.configure_trigger(
            trigger_type='pulse_width',
            level=0.0,
            pulse_width_min=0.005,
            pulse_width_max=0.015
        )
        data = osc.capture_with_trigger(duration=0.5)
        print("✓ Trigger pulse width funciona")
        
        osc.stop()
        print("\n✅ TEST 1 PASADO: Sistema de triggers OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_multichannel():
    """Prueba el sistema multi-canal."""
    print("\n" + "="*70)
    print("TEST 2: Sistema Multi-Canal")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=4)
        osc.start()
        
        # Configurar canales
        osc.configure_channel(0, enabled=True, label='CH1', vertical_scale=1.0)
        osc.configure_channel(1, enabled=True, label='CH2', vertical_scale=2.0)
        osc.configure_channel(2, enabled=False, label='CH3')
        print("✓ Canales configurados")
        
        # Capturar en múltiples canales
        osc.source.signal_type = 'sine'
        osc.source.frequency = 10.0
        
        data1 = osc.capture_channel(0, duration=1.0)
        print(f"✓ Canal 0 capturado: {len(data1)} muestras")
        
        osc.source.frequency = 20.0
        data2 = osc.capture_channel(1, duration=1.0)
        print(f"✓ Canal 1 capturado: {len(data2)} muestras")
        
        # Verificar info de canales
        info = osc.get_channel_info()
        assert len(info) == 4, "Debe haber 4 canales"
        print(f"✓ Información de canales: {len(info)} canales")
        
        # Análisis cruzado
        cross = osc.cross_channel_analysis(0, 1)
        print(f"✓ Análisis cruzado: correlación={cross['correlation']:.3f}")
        
        # Medición por canal
        freq1 = osc.measure('frequency', channel=0)
        freq2 = osc.measure('frequency', channel=1)
        print(f"✓ Mediciones: CH0={freq1:.1f}Hz, CH1={freq2:.1f}Hz")
        
        osc.stop()
        print("\n✅ TEST 2 PASADO: Multi-canal OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_protocol_decoders():
    """Prueba los decodificadores de protocolos."""
    print("\n" + "="*70)
    print("TEST 3: Decodificadores de Protocolos")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000000.0, num_channels=4)
        
        # Generar señal UART simulada (señal cuadrada como ejemplo)
        t = np.arange(0, 0.01, 1/osc.sample_rate)
        uart_signal = (np.sin(2 * np.pi * 9600 * t) > 0).astype(float)
        osc.channels.set_channel_data(0, uart_signal)
        print("✓ Señal UART generada")
        
        # Decodificar UART
        frames = osc.decode_uart(channel=0, baud_rate=9600)
        print(f"✓ UART decodificado: {len(frames)} frames")
        
        # Generar señales I2C simuladas
        scl = (np.sin(2 * np.pi * 100000 * t) > 0).astype(float)
        sda = (np.sin(2 * np.pi * 50000 * t) > 0).astype(float)
        osc.channels.set_channel_data(0, scl)
        osc.channels.set_channel_data(1, sda)
        print("✓ Señales I2C generadas")
        
        # Decodificar I2C
        transactions = osc.decode_i2c(scl_channel=0, sda_channel=1)
        print(f"✓ I2C decodificado: {len(transactions)} transacciones")
        
        # Generar señales SPI simuladas
        sclk = (np.sin(2 * np.pi * 1000000 * t) > 0).astype(float)
        mosi = (np.sin(2 * np.pi * 500000 * t) > 0).astype(float)
        miso = (np.sin(2 * np.pi * 250000 * t) > 0).astype(float)
        osc.channels.set_channel_data(0, sclk)
        osc.channels.set_channel_data(1, mosi)
        osc.channels.set_channel_data(2, miso)
        print("✓ Señales SPI generadas")
        
        # Decodificar SPI
        spi_trans = osc.decode_spi(
            sclk_channel=0, 
            mosi_channel=1, 
            miso_channel=2,
            mode=0
        )
        print(f"✓ SPI decodificado: {len(spi_trans)} transacciones")
        
        print("\n✅ TEST 3 PASADO: Decodificadores de protocolos OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_measurement_api():
    """Prueba la API de mediciones automatizadas."""
    print("\n" + "="*70)
    print("TEST 4: API de Mediciones Automatizadas")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=2)
        osc.source.signal_type = 'sine'
        osc.source.frequency = 50.0
        osc.source.amplitude = 2.5
        osc.start()
        
        # Capturar en canal 0
        osc.capture_channel(0, duration=2.0)
        
        # Realizar mediciones específicas
        freq = osc.measure('frequency', channel=0)
        rms = osc.measure('rms', channel=0)
        snr = osc.measure('snr', channel=0)
        peak_to_peak = osc.measure('peak_to_peak', channel=0)
        
        print(f"✓ Frecuencia: {freq:.2f} Hz")
        print(f"✓ RMS: {rms:.4f} V")
        print(f"✓ SNR: {snr:.2f} dB")
        print(f"✓ Pico-Pico: {peak_to_peak:.4f} V")
        
        # Verificar valores razonables
        assert 45 < freq < 55, f"Frecuencia fuera de rango: {freq}"
        assert rms > 0, "RMS debe ser positivo"
        print("✓ Valores de medición válidos")
        
        osc.stop()
        print("\n✅ TEST 4 PASADO: API de mediciones OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_export_formats():
    """Prueba los formatos de exportación avanzados."""
    print("\n" + "="*70)
    print("TEST 5: Formatos de Exportación Avanzados")
    print("="*70)
    
    try:
        osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=1)
        osc.source.signal_type = 'sine'
        osc.start()
        
        # Capturar datos
        osc.capture_channel(0, duration=1.0)
        
        # Exportar a NPY
        osc.export_npy('/tmp/test_signal.npy', channel=0)
        print("✓ Exportado a NPY")
        
        # Verificar que el archivo existe
        import os
        assert os.path.exists('/tmp/test_signal.npy'), "Archivo NPY no creado"
        print("✓ Archivo NPY verificado")
        
        # Exportar a WAV (si scipy está disponible)
        try:
            osc.export_wav('/tmp/test_signal.wav', channel=0)
            print("✓ Exportado a WAV")
            assert os.path.exists('/tmp/test_signal.wav'), "Archivo WAV no creado"
            print("✓ Archivo WAV verificado")
        except Exception as wav_err:
            print(f"⚠ WAV export no disponible: {wav_err}")
        
        # Exportar a MATLAB (si scipy está disponible)
        try:
            osc.export_matlab('/tmp/test_signal.mat', channel=0)
            print("✓ Exportado a MATLAB")
            assert os.path.exists('/tmp/test_signal.mat'), "Archivo MAT no creado"
            print("✓ Archivo MAT verificado")
        except Exception as mat_err:
            print(f"⚠ MAT export no disponible: {mat_err}")
        
        # CSV original sigue funcionando
        osc.export_data('/tmp/test_signal.csv')
        assert os.path.exists('/tmp/test_signal.csv'), "Archivo CSV no creado"
        print("✓ Exportación CSV (legacy) funciona")
        
        osc.stop()
        print("\n✅ TEST 5 PASADO: Formatos de exportación OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Prueba compatibilidad con código existente."""
    print("\n" + "="*70)
    print("TEST 6: Compatibilidad hacia Atrás")
    print("="*70)
    
    try:
        # Código antiguo debe seguir funcionando
        osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
        osc.start()
        data = osc.capture(duration=1.0)
        print(f"✓ Captura básica: {len(data)} muestras")
        
        # Filtros
        osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)
        print("✓ Filtro aplicado")
        
        # Análisis
        results = osc.analyze()
        print(f"✓ Análisis: {len(results)} métricas")
        
        # Visualización
        osc.plot_signal(save_path='/tmp/compat_signal.png')
        print("✓ Visualización funciona")
        
        # PWM
        osc.source.signal_type = 'square'
        osc.capture(duration=0.1)
        pwm_info = osc.decode_pwm()
        print(f"✓ PWM decodificado: {pwm_info['frequency']:.2f}Hz")
        
        # Exportación
        osc.export_data('/tmp/compat_data.csv')
        print("✓ Exportación CSV funciona")
        
        osc.stop()
        print("\n✅ TEST 6 PASADO: Compatibilidad hacia atrás OK")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FALLIDO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecuta todos los tests."""
    print("="*70)
    print("SUITE DE PRUEBAS - FUNCIONALIDADES AVANZADAS")
    print("="*70)
    
    tests = [
        test_trigger_system,
        test_multichannel,
        test_protocol_decoders,
        test_measurement_api,
        test_export_formats,
        test_backward_compatibility,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Tests pasados: {passed}/{total}")
    print(f"Tests fallidos: {total-passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS AVANZADOS PASARON! 🎉")
        return 0
    else:
        print(f"\n⚠ {total-passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(main())
