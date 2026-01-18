#!/usr/bin/env python3
"""
Ejemplo completo de las funcionalidades avanzadas del osciloscopio digital.

Este ejemplo demuestra:
1. Triggers avanzados
2. Multi-canal
3. Decodificación de protocolos
4. Persistencia digital
5. Análisis espectral avanzado (STFT, Welch)
6. Calibración y modelo de ruido
7. Exportación en múltiples formatos
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from osciloscopio import (
    DigitalOscilloscope,
    FilterType,
    TriggerType,
)


def demo_advanced_triggers():
    """Demuestra el sistema de triggers avanzado."""
    print("\n" + "="*70)
    print("DEMO 1: Triggers Avanzados")
    print("="*70)
    
    # Crear osciloscopio
    osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
    osc.source.signal_type = 'square'
    osc.source.frequency = 50.0
    osc.start()
    
    # Trigger en flanco de subida
    print("\n1. Trigger en flanco de subida:")
    osc.configure_trigger(
        trigger_type='rising_edge',
        level=0.0,
        mode='normal',
        hysteresis=0.1
    )
    data = osc.capture_with_trigger(duration=0.5, pre_trigger_percent=10.0)
    print(f"   Capturado: {len(data)} muestras")
    
    # Trigger en flanco de bajada
    print("\n2. Trigger en flanco de bajada:")
    osc.configure_trigger(trigger_type='falling_edge', level=0.0)
    data = osc.capture_with_trigger(duration=0.5)
    print(f"   Capturado: {len(data)} muestras")
    
    # Trigger por ancho de pulso
    print("\n3. Trigger por ancho de pulso (5-15ms):")
    osc.configure_trigger(
        trigger_type='pulse_width',
        level=0.0,
        pulse_width_min=0.005,
        pulse_width_max=0.015
    )
    data = osc.capture_with_trigger(duration=0.5)
    print(f"   Capturado: {len(data)} muestras")
    
    osc.stop()
    print("\n✓ Demo de triggers completada")


def demo_multichannel():
    """Demuestra el sistema multi-canal."""
    print("\n" + "="*70)
    print("DEMO 2: Sistema Multi-Canal")
    print("="*70)
    
    # Crear osciloscopio con 4 canales
    osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=4)
    osc.start()
    
    # Configurar canales
    print("\n1. Configurando 4 canales:")
    osc.configure_channel(0, enabled=True, label='Señal A', vertical_scale=1.0, color='blue')
    osc.configure_channel(1, enabled=True, label='Señal B', vertical_scale=2.0, color='red')
    osc.configure_channel(2, enabled=True, label='Señal C', vertical_scale=1.5, color='green')
    osc.configure_channel(3, enabled=False, label='Reserva')
    print("   Canales configurados")
    
    # Capturar diferentes señales en cada canal
    print("\n2. Capturando señales diferentes:")
    osc.source.signal_type = 'sine'
    osc.source.frequency = 10.0
    osc.capture_channel(0, duration=2.0)
    print("   Canal 0: Seno 10Hz")
    
    osc.source.frequency = 20.0
    osc.capture_channel(1, duration=2.0)
    print("   Canal 1: Seno 20Hz")
    
    osc.source.signal_type = 'square'
    osc.source.frequency = 15.0
    osc.capture_channel(2, duration=2.0)
    print("   Canal 2: Cuadrada 15Hz")
    
    # Mediciones por canal
    print("\n3. Mediciones automatizadas por canal:")
    for ch in [0, 1, 2]:
        freq = osc.measure('frequency', channel=ch)
        rms = osc.measure('rms', channel=ch)
        print(f"   Canal {ch}: f={freq:.2f}Hz, RMS={rms:.4f}V")
    
    # Análisis cruzado
    print("\n4. Análisis cruzado Canal 0 vs Canal 1:")
    cross = osc.cross_channel_analysis(0, 1)
    print(f"   Correlación: {cross['correlation']:.3f}")
    print(f"   Diferencia de fase: {cross['phase_difference_deg']:.2f}°")
    print(f"   Delay: {cross['delay_time_s']*1000:.2f}ms")
    
    # Información de canales
    print("\n5. Estado de los canales:")
    for info in osc.get_channel_info():
        if info['enabled']:
            print(f"   {info['label']}: {info['samples']} muestras, "
                  f"rango=[{info['min']:.2f}, {info['max']:.2f}]")
    
    osc.stop()
    print("\n✓ Demo multi-canal completada")


def demo_protocol_decoders():
    """Demuestra los decodificadores de protocolos."""
    print("\n" + "="*70)
    print("DEMO 3: Decodificadores de Protocolos")
    print("="*70)
    
    osc = DigitalOscilloscope(sample_rate=1000000.0, num_channels=4)
    
    # Simular señal UART
    print("\n1. Decodificando UART:")
    t = np.arange(0, 0.01, 1/osc.sample_rate)
    uart_signal = (np.sin(2 * np.pi * 9600 * t) > 0).astype(float)
    osc.channels.set_channel_data(0, uart_signal)
    
    frames = osc.decode_uart(channel=0, baud_rate=9600, data_bits=8)
    print(f"   Frames decodificados: {len(frames)}")
    if frames:
        print(f"   Primer frame: 0x{frames[0].data:02X}")
    
    # Simular señales SPI
    print("\n2. Decodificando SPI:")
    sclk = (np.sin(2 * np.pi * 1000000 * t) > 0).astype(float)
    mosi = (np.sin(2 * np.pi * 500000 * t) > 0).astype(float)
    miso = (np.sin(2 * np.pi * 250000 * t) > 0).astype(float)
    osc.channels.set_channel_data(0, sclk)
    osc.channels.set_channel_data(1, mosi)
    osc.channels.set_channel_data(2, miso)
    
    spi_trans = osc.decode_spi(sclk_channel=0, mosi_channel=1, miso_channel=2, mode=0)
    print(f"   Transacciones SPI: {len(spi_trans)}")
    if spi_trans:
        print(f"   Primera transacción: MOSI=0x{spi_trans[0].mosi_data:02X}, "
              f"MISO=0x{spi_trans[0].miso_data:02X}")
    
    print("\n✓ Demo de decodificadores completada")


def demo_persistence():
    """Demuestra el modo de persistencia digital."""
    print("\n" + "="*70)
    print("DEMO 4: Persistencia Digital")
    print("="*70)
    
    osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
    osc.source.signal_type = 'sine'
    osc.source.frequency = 50.0
    osc.source.noise_level = 0.2  # Añadir ruido para ver jitter
    osc.start()
    
    # Habilitar persistencia
    print("\n1. Habilitando persistencia (para análisis de jitter):")
    osc.enable_persistence(width=1000, height=500)
    
    # Capturar múltiples trazas
    print("\n2. Capturando 50 trazas con ruido:")
    for i in range(50):
        data = osc.capture(duration=0.1)
        osc.add_to_persistence(data, decay=True)
    
    # Obtener estadísticas
    print("\n3. Estadísticas de persistencia:")
    stats = osc.get_persistence_stats()
    print(f"   Total de capturas: {stats['num_captures']}")
    print(f"   Hits totales: {stats['total_hits']}")
    print(f"   Hits máximos en un punto: {stats['max_hits']}")
    print(f"   Media de hits: {stats['mean_hits']:.2f}")
    print(f"   Amplitud más común: {stats['most_common_amplitude']:.4f}V")
    
    osc.stop()
    print("\n✓ Demo de persistencia completada")


def demo_spectral_analysis():
    """Demuestra el análisis espectral avanzado."""
    print("\n" + "="*70)
    print("DEMO 5: Análisis Espectral Avanzado")
    print("="*70)
    
    osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
    osc.source.signal_type = 'mixed'  # Señal con armónicos
    osc.source.frequency = 50.0
    osc.start()
    
    # Capturar señal
    print("\n1. Capturando señal compleja (con armónicos):")
    osc.capture_channel(0, duration=2.0)
    
    # STFT
    print("\n2. Calculando STFT (Short-Time Fourier Transform):")
    f, t, Zxx = osc.compute_stft(channel=0, window_size=256, overlap=128)
    print(f"   Dimensiones del espectrograma: {Zxx.shape}")
    print(f"   Rango de frecuencias: 0-{f[-1]:.1f}Hz")
    print(f"   Duración temporal: {t[-1]:.2f}s")
    
    # Welch PSD
    print("\n3. Calculando PSD (Welch):")
    f_psd, psd = osc.compute_welch_psd(channel=0, window_size=512)
    peak_idx = np.argmax(psd)
    print(f"   Frecuencia pico: {f_psd[peak_idx]:.2f}Hz")
    print(f"   Potencia pico: {psd[peak_idx]:.2e}")
    
    # Análisis de armónicos
    print("\n4. Análisis detallado de armónicos:")
    harm = osc.harmonic_analysis(channel=0, fundamental_freq=50.0, num_harmonics=5)
    print(f"   Frecuencia fundamental: {harm['fundamental_frequency']:.2f}Hz")
    print(f"   Amplitud fundamental: {harm['fundamental_amplitude']:.4f}V")
    print(f"   THD: {harm['thd']:.4f} ({harm['thd_db']:.2f}dB)")
    print("\n   Armónicos detectados:")
    for h in sorted(harm['harmonics'].keys()):
        h_data = harm['harmonics'][h]
        print(f"     {h}: {h_data['frequency']:.2f}Hz, "
              f"{h_data['amplitude']:.4f}V ({h_data['amplitude_db']:.2f}dB)")
    
    osc.stop()
    print("\n✓ Demo de análisis espectral completada")


def demo_calibration():
    """Demuestra el sistema de calibración."""
    print("\n" + "="*70)
    print("DEMO 6: Sistema de Calibración")
    print("="*70)
    
    osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=1)
    osc.source.signal_type = 'sine'
    osc.source.frequency = 10.0
    osc.start()
    
    # Configurar modelo de ruido
    print("\n1. Configurando modelo de ruido:")
    osc.set_noise_model(thermal=0.02, shot=0.01, flicker=0.005)
    print("   Ruido térmico: 0.02")
    print("   Ruido shot: 0.01")
    print("   Ruido flicker: 0.005")
    
    # Capturar señal de tierra para calibrar offset
    print("\n2. Calibrando offset (señal en tierra):")
    osc.source.amplitude = 0.0
    ground_data = osc.capture(duration=1.0)
    osc.calibrate(ground_signal=ground_data)
    
    # Capturar señal conocida para calibrar ganancia
    print("\n3. Calibrando ganancia (señal de 5V):")
    osc.source.amplitude = 5.0
    known_data = osc.capture(duration=1.0)
    osc.calibrate(known_signal=known_data, known_amplitude=5.0)
    
    # Aplicar calibración
    print("\n4. Aplicando calibración a canal 0:")
    osc.source.amplitude = 2.5
    osc.capture_channel(0, duration=1.0)
    osc.apply_calibration_to_channel(0)
    
    # Estado del sistema
    print("\n5. Estado completo del sistema:")
    status = osc.get_system_status()
    print(f"   Sample rate: {status['sample_rate']}Hz")
    print(f"   Canales: {status['num_channels']}")
    print(f"   Fuente: {status['source_type']}")
    print(f"   Calibrado: {status['calibration']['is_calibrated']}")
    print(f"   Offset: {status['calibration']['offset']:.6f}")
    print(f"   Ganancia: {status['calibration']['gain']:.6f}")
    
    osc.stop()
    print("\n✓ Demo de calibración completada")


def demo_export_formats():
    """Demuestra la exportación en múltiples formatos."""
    print("\n" + "="*70)
    print("DEMO 7: Exportación en Múltiples Formatos")
    print("="*70)
    
    osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=1)
    osc.source.signal_type = 'sine'
    osc.source.frequency = 50.0
    osc.start()
    
    # Capturar datos
    print("\n1. Capturando señal de prueba:")
    osc.capture_channel(0, duration=2.0)
    print("   Señal capturada: 2000 muestras")
    
    # Exportar en diferentes formatos
    print("\n2. Exportando en múltiples formatos:")
    
    # CSV (compatible con Excel, MATLAB, etc.)
    osc.export_data('/tmp/signal.csv', use_filtered=False)
    print("   ✓ CSV: /tmp/signal.csv")
    
    # NumPy (para procesamiento en Python)
    osc.export_npy('/tmp/signal.npy', channel=0)
    print("   ✓ NPY: /tmp/signal.npy")
    
    # WAV (para análisis de audio)
    try:
        osc.export_wav('/tmp/signal.wav', channel=0)
        print("   ✓ WAV: /tmp/signal.wav")
    except Exception as e:
        print(f"   ⚠ WAV: No disponible ({e})")
    
    # MATLAB
    try:
        osc.export_matlab('/tmp/signal.mat', channel=0)
        print("   ✓ MAT: /tmp/signal.mat")
    except Exception as e:
        print(f"   ⚠ MAT: No disponible ({e})")
    
    osc.stop()
    print("\n✓ Demo de exportación completada")


def main():
    """Ejecuta todas las demos."""
    print("="*70)
    print("DEMOS DE FUNCIONALIDADES AVANZADAS")
    print("Osciloscopio Digital - Herramienta Profesional de Prototipado")
    print("="*70)
    
    demos = [
        demo_advanced_triggers,
        demo_multichannel,
        demo_protocol_decoders,
        demo_persistence,
        demo_spectral_analysis,
        demo_calibration,
        demo_export_formats,
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Error en demo: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print("TODAS LAS DEMOS COMPLETADAS")
    print("="*70)
    print("\nEl osciloscopio digital ahora incluye:")
    print("  ✓ Triggers avanzados (rising, falling, pulse width, runt, window)")
    print("  ✓ Soporte multi-canal (hasta 8 canales)")
    print("  ✓ Decodificadores de protocolos (UART, I2C, SPI, CAN, PWM)")
    print("  ✓ Persistencia digital (análisis de jitter)")
    print("  ✓ Análisis espectral avanzado (STFT, Welch, armónicos)")
    print("  ✓ Sistema de calibración (offset, ganancia, ruido)")
    print("  ✓ Exportación múltiple (CSV, NPY, WAV, MAT)")
    print("\n¡Listo para prototipado profesional!")


if __name__ == "__main__":
    main()
