# Guía Rápida: Nuevas Funcionalidades Avanzadas v0.2.0

## 🚀 De Osciloscopio Educativo a Herramienta Profesional

Esta guía resume las nuevas funcionalidades que transforman el osciloscopio en una herramienta seria para prototipado electrónico.

## ⚡ Inicio Rápido - 30 Segundos

```python
from osciloscopio import DigitalOscilloscope

# Crear osciloscopio con 4 canales
osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=4)

# Configurar trigger en rising edge
osc.configure_trigger(trigger_type='rising_edge', level=0.0, mode='normal')

# Capturar con trigger
osc.start()
data = osc.capture_with_trigger(duration=0.5)

# Medir frecuencia en canal 0
freq = osc.measure('frequency', channel=0)
print(f"Frecuencia: {freq:.2f}Hz")

osc.stop()
```

## 📋 Resumen de Características

### 1. Triggers Avanzados ⚡
**Problema resuelto**: Capturar exactamente lo que necesitas, cuando lo necesitas.

```python
# Rising edge con holdoff
osc.configure_trigger(
    trigger_type='rising_edge',
    level=0.5,
    mode='normal',
    hysteresis=0.1,
    holdoff=0.01  # 10ms entre triggers
)

# Pulse width (5-15ms)
osc.configure_trigger(
    trigger_type='pulse_width',
    level=0.0,
    pulse_width_min=0.005,
    pulse_width_max=0.015
)
```

**Tipos disponibles**: rising_edge, falling_edge, either_edge, pulse_width, runt_pulse, window

### 2. Multi-Canal 📊
**Problema resuelto**: Comparar señales entre sí, análisis de fase, correlación.

```python
# 4 canales configurables
osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=4)

# Configurar cada canal
osc.configure_channel(0, label='Voltaje', vertical_scale=1.0, coupling='dc')
osc.configure_channel(1, label='Corriente', vertical_scale=2.0, coupling='ac')

# Capturar en múltiples canales
osc.capture_channel(0, duration=2.0)
osc.capture_channel(1, duration=2.0)

# Análisis cruzado
cross = osc.cross_channel_analysis(0, 1)
print(f"Fase: {cross['phase_difference_deg']:.2f}°")
print(f"Correlación: {cross['correlation']:.3f}")
```

### 3. Decodificadores de Protocolos 🔌
**Problema resuelto**: Entender comunicación digital sin osciloscopio de $5000.

```python
osc = DigitalOscilloscope(sample_rate=1000000.0, num_channels=4)

# UART (async serial)
frames = osc.decode_uart(channel=0, baud_rate=115200, data_bits=8)
text = osc.protocol_decoder.uart_decoder.frames_to_string(frames)

# I2C (SCL=canal 0, SDA=canal 1)
transactions = osc.decode_i2c(scl_channel=0, sda_channel=1)

# SPI (SCLK=0, MOSI=1, MISO=2, CS=3)
spi = osc.decode_spi(0, 1, 2, 3, mode=0, bits_per_word=8)

# CAN (básico)
can_frames = osc.protocol_decoder.decode_can(data)
```

**Protocolos soportados**: UART, I²C, SPI, CAN, PWM

### 4. Mediciones Automatizadas 📏
**Problema resuelto**: API simple tipo `measure('frequency', channel=1)`

```python
# Mediciones instantáneas por canal
freq = osc.measure('frequency', channel=0)
rms = osc.measure('rms', channel=1)
snr = osc.measure('snr', channel=2)
thd = osc.measure('thd', channel=0)

print(f"CH0: {freq:.2f}Hz")
print(f"CH1: {rms:.4f}V RMS")
print(f"CH2: {snr:.2f}dB SNR")
```

**Métricas disponibles**: frequency, rms, peak_to_peak, snr, thd, duty_cycle, rise_time, fall_time, mean, std, min, max, period, variance

### 5. Persistencia Digital 🎨
**Problema resuelto**: Ver jitter, variaciones estadísticas, eye diagrams.

```python
# Habilitar persistencia
osc.enable_persistence(width=1000, height=500)

# Capturar múltiples trazas
for i in range(100):
    data = osc.capture(duration=0.1)
    osc.add_to_persistence(data, decay=True)

# Analizar variaciones
stats = osc.get_persistence_stats()
print(f"Capturas: {stats['num_captures']}")
print(f"Jitter visible en hits: {stats['max_hits']} pico")
```

### 6. Análisis Espectral Avanzado 🌊
**Problema resuelto**: STFT, Welch, armónicos, más allá de FFT básico.

```python
# STFT (tiempo-frecuencia)
f, t, Zxx = osc.compute_stft(channel=0, window_size=256)

# Welch PSD (mejor que FFT para ruido)
f_psd, psd = osc.compute_welch_psd(channel=0, window_size=512)

# Análisis de armónicos detallado
harm = osc.harmonic_analysis(channel=0, fundamental_freq=50.0, num_harmonics=10)
print(f"THD: {harm['thd']:.4f}")
for h in harm['harmonics']:
    print(f"{h}: {harm['harmonics'][h]['amplitude']:.4f}V")
```

### 7. Calibración y Ruido 🎯
**Problema resuelto**: Compensar offset/ganancia, modelar ruido realista.

```python
# Calibrar offset (con entrada en tierra)
ground_data = osc.capture(duration=1.0)
osc.calibrate(ground_signal=ground_data)

# Calibrar ganancia (con señal de 5V conocida)
known_data = osc.capture(duration=1.0)
osc.calibrate(known_signal=known_data, known_amplitude=5.0)

# Modelo de ruido
osc.set_noise_model(thermal=0.02, shot=0.01, flicker=0.005)

# Aplicar calibración
osc.apply_calibration_to_channel(0)
```

### 8. Exportación Profesional 💾
**Problema resuelto**: Trabajar con datos en otras herramientas (Python, MATLAB, Excel).

```python
# Múltiples formatos
osc.export_data('signal.csv')       # Excel, universal
osc.export_npy('signal.npy')        # NumPy/Python
osc.export_wav('signal.wav')        # Audio, DSP
osc.export_matlab('signal.mat')     # MATLAB

# Cargar en Python
import numpy as np
data = np.load('signal.npy')

# Cargar en MATLAB
# >> load('signal.mat');
# >> plot(signal);
```

## 🎓 Casos de Uso

### Caso 1: Depurar Bus I2C
```python
osc = DigitalOscilloscope(sample_rate=10000000.0, num_channels=2)

# Capturar comunicación I2C
osc.capture_channel(0, duration=0.01)  # SCL
osc.capture_channel(1, duration=0.01)  # SDA

# Decodificar
transactions = osc.decode_i2c(0, 1)

# Ver transacciones
for t in transactions:
    if t.operation.value == 'write':
        print(f"Escribir a 0x{t.address:02X}: 0x{t.data:02X}")
```

### Caso 2: Medir THD de Amplificador de Audio
```python
osc = DigitalOscilloscope(sample_rate=48000.0, num_channels=2)

# Capturar entrada y salida
osc.capture_channel(0, duration=1.0)  # Input
osc.capture_channel(1, duration=1.0)  # Output

# Análisis de armónicos
harm_in = osc.harmonic_analysis(0, fundamental_freq=1000.0)
harm_out = osc.harmonic_analysis(1, fundamental_freq=1000.0)

print(f"THD entrada: {harm_in['thd']:.4f}")
print(f"THD salida: {harm_out['thd']:.4f}")
print(f"Distorsión introducida: {(harm_out['thd']-harm_in['thd'])*100:.2f}%")
```

### Caso 3: Análisis de Jitter en Clock
```python
osc = DigitalOscilloscope(sample_rate=100000000.0, num_channels=1)

# Configurar trigger en rising edge
osc.configure_trigger(trigger_type='rising_edge', level=1.65)

# Persistencia para ver jitter
osc.enable_persistence(1000, 500)

# Capturar 500 ciclos
for i in range(500):
    data = osc.capture_with_trigger(duration=0.0001)
    osc.add_to_persistence(data)

# Estadísticas de jitter
stats = osc.get_persistence_stats()
# El spread en el histograma muestra el jitter
```

## 📊 Comparación de Capacidades

| Característica | v0.1.0 (Antes) | v0.2.0 (Ahora) |
|---------------|----------------|----------------|
| Canales | 1 | 1-8 |
| Triggers | Ninguno | 6 tipos avanzados |
| Protocolos | PWM básico | UART, I²C, SPI, CAN, PWM |
| Mediciones | Manual | `measure('metric', ch)` |
| Análisis espectral | FFT | FFT, STFT, Welch, armónicos |
| Persistencia | No | Sí (jitter analysis) |
| Calibración | No | Offset/Gain + ruido |
| Exportación | CSV | CSV, NPY, WAV, MAT |
| Análisis cruzado | No | Fase, correlación, delay |

## 🎯 La Tríada de Impacto

Según el problema statement, estas son las 3 features que convierten un osciloscopio "bonito" en uno "útil":

1. ✅ **Triggers avanzados** - Implementado (6 tipos)
2. ✅ **Multi-canal** - Implementado (hasta 8)
3. ✅ **Decodificadores** - Implementado (5 protocolos)

**Plus el "moño nerd":**
4. ✅ **Persistencia** - Implementado
5. ✅ **STFT** - Implementado
6. ✅ **Calibración** - Implementado
7. ✅ **API** - Implementado

## 🔗 Recursos

- **README completo**: `/README.md`
- **Ejemplos básicos**: `/examples/basic_example.py`
- **Demo avanzada**: `/examples/advanced_features_demo.py`
- **Tests**: `test_oscilloscope.py` y `test_advanced_features.py`

## 💪 Próximos Pasos Sugeridos

Para convertirlo en producto comercial:
- [ ] WebSocket API para control remoto
- [ ] Plugin system para extensibilidad
- [ ] GUI con PyQt o web (React)
- [ ] Wavelets (más avanzado que STFT)
- [ ] Modo streaming real continuo
- [ ] Integración con hardware popular (Arduino, ESP32, STM32)

¡Ya tienes una herramienta seria para prototipado! 🚀
