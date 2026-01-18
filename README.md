# Osciloscopio Digital Profesional 📊

Sistema completo de osciloscopio digital para prototipado electrónico profesional: captura multi-canal, decodifica protocolos, triggers avanzados, análisis espectral y persistencia digital. 

**De osciloscopio educativo a herramienta seria para prototipado.**

## 🎯 Características

### 🚀 Funcionalidades Avanzadas (NUEVO v0.2.0)

#### Triggers Avanzados
- **Rising Edge**: Trigger en flanco de subida con histéresis configurable
- **Falling Edge**: Trigger en flanco de bajada
- **Either Edge**: Trigger en cualquier flanco
- **Pulse Width**: Captura pulsos de ancho específico (min-max)
- **Runt Pulse**: Detecta pulsos que no alcanzan el nivel esperado
- **Window Trigger**: Trigger cuando la señal sale de una ventana definida
- **Modos**: Auto, Normal, Single con holdoff configurable

#### Soporte Multi-Canal
- **Hasta 8 canales simultáneos** de captura
- **Configuración independiente** por canal (escala, offset, acoplamiento, etiqueta)
- **Análisis cruzado** entre canales: correlación, diferencia de fase, delay
- **Operaciones matemáticas**: suma, resta, multiplicación, división entre canales
- **Mediciones automatizadas** por canal: `measure('frequency', channel=1)`

#### Decodificadores de Protocolos Digitales
- **UART**: Configurable (baudrate, data bits, paridad, stop bits)
- **I²C**: Decodifica START, STOP, dirección, ACK/NACK, datos
- **SPI**: Modos 0-3, bit order configurable, MOSI/MISO simultáneo
- **CAN**: Decodificación básica de frames (estándar)
- **PWM**: Ciclo de trabajo, frecuencia, período

#### Persistencia Digital
- **Captura estadística** de múltiples trazas
- **Análisis de jitter** y variaciones
- **Histogramas** de amplitud y tiempo
- **Decaimiento configurable** para visualización temporal

#### Análisis Espectral Avanzado
- **STFT**: Short-Time Fourier Transform con ventanas configurables
- **Welch PSD**: Densidad espectral de potencia con reducción de ruido
- **Análisis de Armónicos**: THD, amplitud relativa, hasta 10+ armónicos
- **Frecuencia Instantánea**: Estimación vía transformada de Hilbert
- **Coherencia**: Análisis de coherencia entre canales
- **Filtros Adaptativos**: LMS (Least Mean Squares)

#### Sistema de Calibración
- **Calibración de Offset**: Automática con medición de tierra
- **Calibración de Ganancia**: Con señal de amplitud conocida
- **Modelo de Ruido**: Térmico (Gaussiano), Shot (Poisson), Flicker (1/f)
- **Aplicación automática** de calibración a canales

#### Exportación Profesional
- **CSV**: Compatible con Excel, MATLAB, Python
- **NPY**: Formato nativo de NumPy para procesamiento Python
- **WAV**: Para análisis de audio y procesamiento DSP
- **MAT**: Compatible con MATLAB con metadata
- **Metadata incluida**: Sample rate, canal, configuración

### Captura de Señales
- **Hardware Externo**: Conexión mediante puerto serial para captura de señales reales
- **Fuentes Simuladas**: Generadores de señales para prototipado y pruebas
  - Señales seno, cuadrada, triangular, diente de sierra
  - Señales complejas con múltiples componentes armónicos
  - Control de frecuencia, amplitud y nivel de ruido

### Procesamiento de Señales
- **Filtros Configurables**:
  - Filtros Butterworth: paso bajo, paso alto, paso banda, rechaza banda
  - Filtro de media móvil
  - Filtro de mediana
- **Operaciones**:
  - Eliminación de componente DC
  - Normalización de señales
  - Submuestreo
  - Detección de flancos
  - Decodificación PWM

### Análisis
- Mediciones estadísticas (media, RMS, pico-pico, min, max, desviación estándar)
- Análisis espectral (FFT, frecuencia fundamental)
- Mediciones temporales (período, ciclo de trabajo, tiempos de subida/bajada)
- Relación señal-ruido (SNR)
- Distorsión armónica total (THD)
- Detección de picos

### Visualización Interactiva
- Gráficos en dominio del tiempo
- Espectro de frecuencia (FFT)
- Espectrogramas
- Modo XY (figuras de Lissajous)
- Dashboard completo con múltiples vistas
- Comparación de señales (original vs filtrada)
- Exportación de gráficos en alta resolución

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/osciloscopio.git
cd osciloscopio

# Instalar dependencias
pip install -r requirements.txt

# Instalación del paquete
pip install -e .
```

## 📖 Uso Básico

```python
from osciloscopio import DigitalOscilloscope, FilterType

# Crear osciloscopio con fuente simulada
osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')

# Iniciar captura
osc.start()

# Capturar 2 segundos de datos
data = osc.capture(duration=2.0)

# Analizar señal
osc.print_analysis()

# Aplicar filtro
osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)

# Visualizar
osc.plot_signal()
osc.plot_fft()
osc.create_dashboard()

# Exportar datos
osc.export_data('signal_data.csv')

# Detener captura
osc.stop()
```

## 💡 Ejemplos

### Ejemplo 1: Trigger Avanzado con Rising Edge

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
osc.source.signal_type = 'square'
osc.source.frequency = 50.0
osc.start()

# Configurar trigger en flanco de subida
osc.configure_trigger(
    trigger_type='rising_edge',
    level=0.0,
    mode='normal',
    hysteresis=0.1,
    holdoff=0.01  # 10ms entre triggers
)

# Capturar con trigger (10% pre-trigger)
data = osc.capture_with_trigger(duration=0.5, pre_trigger_percent=10.0)

# Visualizar
osc.plot_signal(save_path='triggered_signal.png')
osc.stop()
```

### Ejemplo 2: Multi-Canal con Análisis Cruzado

```python
from osciloscopio import DigitalOscilloscope

# Crear osciloscopio con 4 canales
osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=4)

# Configurar canales
osc.configure_channel(0, label='Voltaje', vertical_scale=1.0, coupling='dc')
osc.configure_channel(1, label='Corriente', vertical_scale=2.0, coupling='ac')
osc.configure_channel(2, label='Señal RF', vertical_scale=0.5, coupling='dc')

osc.start()

# Capturar en múltiples canales
osc.source.frequency = 50.0
osc.capture_channel(0, duration=2.0)

osc.source.frequency = 100.0
osc.capture_channel(1, duration=2.0)

osc.source.frequency = 150.0
osc.capture_channel(2, duration=2.0)

# Mediciones automatizadas por canal
freq_ch0 = osc.measure('frequency', channel=0)
rms_ch1 = osc.measure('rms', channel=1)
snr_ch2 = osc.measure('snr', channel=2)

print(f"CH0: {freq_ch0:.2f}Hz, CH1: {rms_ch1:.4f}V, CH2 SNR: {snr_ch2:.2f}dB")

# Análisis cruzado entre canales
cross = osc.cross_channel_analysis(0, 1)
print(f"Diferencia de fase: {cross['phase_difference_deg']:.2f}°")
print(f"Correlación: {cross['correlation']:.3f}")

osc.stop()
```

### Ejemplo 3: Decodificación de Protocolos

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=1000000.0, num_channels=4)

# Decodificar UART
# (Asumiendo señal UART en canal 0)
frames = osc.decode_uart(channel=0, baud_rate=115200, data_bits=8, parity='none')
print(f"UART: {len(frames)} frames recibidos")

# Convertir a texto
text = osc.protocol_decoder.uart_decoder.frames_to_string(frames)
print(f"Texto: {text}")

# Decodificar I2C
# (SCL en canal 0, SDA en canal 1)
transactions = osc.decode_i2c(scl_channel=0, sda_channel=1)
for trans in transactions:
    if trans.operation.value == 'write':
        print(f"I2C Write: Addr=0x{trans.address:02X}, Data=0x{trans.data:02X}")

# Decodificar SPI
# (SCLK=0, MOSI=1, MISO=2, CS=3)
spi_trans = osc.decode_spi(
    sclk_channel=0, 
    mosi_channel=1, 
    miso_channel=2,
    cs_channel=3,
    mode=0,
    bits_per_word=8
)
print(f"SPI: {len(spi_trans)} transacciones")
```

### Ejemplo 4: Persistencia Digital (Análisis de Jitter)

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
osc.source.signal_type = 'sine'
osc.source.frequency = 50.0
osc.source.noise_level = 0.1  # Añadir ruido/jitter
osc.start()

# Habilitar persistencia
osc.enable_persistence(width=1000, height=500)

# Capturar 100 trazas para analizar jitter
for i in range(100):
    data = osc.capture(duration=0.1)
    osc.add_to_persistence(data, decay=True)

# Obtener estadísticas de jitter
stats = osc.get_persistence_stats()
print(f"Capturas: {stats['num_captures']}")
print(f"Amplitud más común: {stats['most_common_amplitude']:.4f}V")
print(f"Distribución de hits: max={stats['max_hits']}, mean={stats['mean_hits']:.2f}")

osc.stop()
```

### Ejemplo 5: Análisis Espectral Avanzado (STFT y Armónicos)

```python
from osciloscopio import DigitalOscilloscope
import matplotlib.pyplot as plt
import numpy as np

osc = DigitalOscilloscope(sample_rate=10000.0, num_channels=1)
osc.source.signal_type = 'mixed'  # Señal con armónicos
osc.source.frequency = 50.0
osc.start()

# Capturar señal compleja
osc.capture_channel(0, duration=2.0)

# STFT (Short-Time Fourier Transform)
f, t, Zxx = osc.compute_stft(channel=0, window_size=256, overlap=128)
plt.figure(figsize=(10, 6))
plt.pcolormesh(t, f, 20*np.log10(Zxx + 1e-10), shading='gouraud')
plt.ylabel('Frecuencia (Hz)')
plt.xlabel('Tiempo (s)')
plt.title('STFT - Espectrograma')
plt.colorbar(label='Potencia (dB)')
plt.savefig('stft.png')

# Welch PSD
f_psd, psd = osc.compute_welch_psd(channel=0, window_size=512)
plt.figure()
plt.semilogy(f_psd, psd)
plt.xlabel('Frecuencia (Hz)')
plt.ylabel('PSD')
plt.title('Densidad Espectral de Potencia (Welch)')
plt.savefig('welch_psd.png')

# Análisis detallado de armónicos
harm = osc.harmonic_analysis(channel=0, fundamental_freq=50.0, num_harmonics=10)
print(f"Frecuencia fundamental: {harm['fundamental_frequency']:.2f}Hz")
print(f"THD: {harm['thd']:.4f} ({harm['thd_db']:.2f}dB)")
print("\nArmónicos:")
for h in sorted(harm['harmonics'].keys()):
    h_data = harm['harmonics'][h]
    print(f"  {h}: {h_data['frequency']:.2f}Hz, {h_data['amplitude']:.4f}V")

osc.stop()
```

### Ejemplo 6: Calibración y Modelo de Ruido

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=1)
osc.start()

# 1. Calibrar offset (con entrada en tierra)
osc.source.amplitude = 0.0
ground_data = osc.capture(duration=1.0)
osc.calibrate(ground_signal=ground_data)

# 2. Calibrar ganancia (con señal de 5V conocida)
osc.source.amplitude = 5.0
known_data = osc.capture(duration=1.0)
osc.calibrate(known_signal=known_data, known_amplitude=5.0)

# 3. Configurar modelo de ruido
osc.set_noise_model(
    thermal=0.02,   # Ruido térmico
    shot=0.01,      # Ruido shot
    flicker=0.005   # Ruido flicker (1/f)
)

# 4. Capturar y aplicar calibración
osc.source.amplitude = 2.5
osc.capture_channel(0, duration=1.0)
osc.apply_calibration_to_channel(0)

# Ver estado de calibración
status = osc.get_system_status()
print(f"Calibrado: {status['calibration']['is_calibrated']}")
print(f"Offset: {status['calibration']['offset']:.6f}V")
print(f"Ganancia: {status['calibration']['gain']:.6f}")

osc.stop()
```

### Ejemplo 7: Exportación Múltiple

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=1000.0, num_channels=1)
osc.source.signal_type = 'sine'
osc.source.frequency = 50.0
osc.start()

# Capturar datos
osc.capture_channel(0, duration=2.0)

# Exportar en diferentes formatos
osc.export_data('signal.csv')           # CSV para Excel
osc.export_npy('signal.npy')            # NumPy para Python
osc.export_wav('signal.wav')            # WAV para audio
osc.export_matlab('signal.mat')         # MAT para MATLAB

osc.stop()

# Cargar datos en Python
import numpy as np
data = np.load('signal.npy')
print(f"Datos cargados: {len(data)} muestras")

# Cargar en MATLAB:
# >> data = load('signal.mat');
# >> plot(data.signal);
```

### Ejemplo 8: Análisis de Señales Simuladas

```python
from osciloscopio import DigitalOscilloscope, FilterType

osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')

# Configurar parámetros de la señal
osc.set_source_parameters(
    frequency=50.0,
    amplitude=3.0,
    noise_level=0.1
)

osc.start()
osc.capture(duration=2.0)

# Análisis completo
results = osc.analyze()
print(f"Frecuencia: {results['frequency']:.2f} Hz")
print(f"RMS: {results['rms']:.4f} V")
print(f"SNR: {results['snr']:.2f} dB")

# Visualización
osc.plot_signal(save_path='signal.png')
osc.plot_fft(save_path='fft.png')
```

## 📁 Estructura del Proyecto

```
osciloscopio/
├── osciloscopio/
│   ├── __init__.py              # Inicialización del paquete
│   ├── acquisition.py           # Captura de señales (hardware/simulado)
│   ├── processing.py            # Filtros y procesamiento
│   ├── visualization.py         # Visualización interactiva
│   ├── analyzer.py              # Análisis y mediciones
│   ├── oscilloscope.py          # Clase principal (orquestador)
│   ├── trigger.py               # ⭐ Sistema de triggers avanzado
│   ├── multichannel.py          # ⭐ Gestor multi-canal
│   ├── protocols.py             # ⭐ Decodificadores de protocolos
│   └── advanced_analysis.py     # ⭐ Persistencia, STFT, calibración
├── examples/
│   ├── basic_example.py         # Ejemplo básico
│   ├── advanced_example.py      # Ejemplos avanzados
│   ├── hardware_example.py      # Captura desde hardware
│   └── advanced_features_demo.py # ⭐ Demo completo de nuevas features
├── test_oscilloscope.py         # Tests básicos
├── test_advanced_features.py    # ⭐ Tests de features avanzadas
├── requirements.txt             # Dependencias
├── setup.py                     # Configuración del paquete
└── README.md                    # Documentación
```

**⭐ = Nuevos módulos v0.2.0**

## 🔧 Módulos

### acquisition.py
Gestiona la captura de señales desde diferentes fuentes:
- `SignalSource`: Clase base abstracta
- `HardwareSource`: Captura desde puerto serial
- `SimulatedSource`: Generador de señales simuladas

### processing.py
Procesamiento de señales con filtros configurables:
- Filtros Butterworth (lowpass, highpass, bandpass, bandstop)
- Filtros estadísticos (media móvil, mediana)
- Operaciones auxiliares (normalización, submuestreo, detección de flancos)
- Decodificación PWM

### visualization.py
Visualización interactiva de señales:
- Gráficos temporales
- Análisis espectral (FFT)
- Espectrogramas
- Modo XY
- Dashboards multipanel

### analyzer.py
Análisis y mediciones de señales:
- Estadísticas básicas (media, RMS, pico-pico, desviación estándar)
- Análisis de frecuencia (FFT, frecuencia fundamental, período)
- Mediciones temporales (ciclo de trabajo, rise/fall time)
- Calidad de señal (SNR, THD)
- Detección de picos

### oscilloscope.py
Clase principal que integra todos los módulos y proporciona una interfaz unificada.

### ⭐ trigger.py (NUEVO)
Sistema de triggers avanzado para captura condicional:
- `TriggerSystem`: Gestor de triggers
- `TriggerType`: Rising/Falling edge, pulse width, runt, window
- `TriggerMode`: Auto, Normal, Single
- `TriggerConfig`: Configuración completa con holdoff

### ⭐ multichannel.py (NUEVO)
Gestor de múltiples canales de captura:
- `MultiChannelManager`: Gestor de hasta 8 canales
- `ChannelConfig`: Configuración por canal (escala, offset, acoplamiento)
- `CouplingMode`: DC, AC, GND
- Análisis cruzado entre canales
- Operaciones matemáticas entre canales

### ⭐ protocols.py (NUEVO)
Decodificadores de protocolos digitales:
- `UARTDecoder`: Decodificación UART completa
- `I2CDecoder`: Decodificación I2C (START, STOP, dirección, datos)
- `SPIDecoder`: Decodificación SPI (modos 0-3)
- `CANDecoder`: Decodificación CAN básica
- `ProtocolDecoder`: Interfaz unificada

### ⭐ advanced_analysis.py (NUEVO)
Análisis espectral avanzado y persistencia:
- `DigitalPersistence`: Sistema de persistencia para análisis de jitter
- `AdvancedSpectralAnalysis`: STFT, Welch PSD, armónicos, coherencia
- `CalibrationSystem`: Calibración de offset/ganancia y modelo de ruido

## 🎓 Tipos de Señales Soportadas

| Tipo | Descripción |
|------|-------------|
| `sine` | Onda sinusoidal pura |
| `square` | Onda cuadrada |
| `triangle` | Onda triangular |
| `sawtooth` | Onda diente de sierra |
| `mixed` | Señal compleja con múltiples armónicos |

## 🔍 Filtros Disponibles

| Filtro | Parámetros | Descripción |
|--------|-----------|-------------|
| `LOWPASS` | `cutoff`, `order` | Elimina frecuencias altas |
| `HIGHPASS` | `cutoff`, `order` | Elimina frecuencias bajas |
| `BANDPASS` | `lowcut`, `highcut`, `order` | Permite banda de frecuencias |
| `BANDSTOP` | `lowcut`, `highcut`, `order` | Rechaza banda de frecuencias |
| `MOVING_AVERAGE` | `window_size` | Suavizado por media móvil |
| `MEDIAN` | `kernel_size` | Filtro de mediana |

## 📊 Métricas de Análisis

- **Media (DC)**: Componente de corriente continua
- **RMS**: Valor eficaz de la señal
- **Pico-pico**: Diferencia entre máximo y mínimo
- **Desviación estándar**: Dispersión de los datos
- **Frecuencia fundamental**: Componente principal del espectro
- **Período**: Tiempo de un ciclo completo
- **Ciclo de trabajo**: Porcentaje en estado alto (señales digitales)
- **Tiempos de subida/bajada**: Velocidad de transición
- **SNR**: Relación señal-ruido en dB
- **THD**: Distorsión armónica total

## 🔌 Conexión con Hardware

Para conectar hardware externo mediante puerto serial:

1. **Arduino o microcontrolador**: Enviar valores de voltaje por serial
2. **Formato**: Un valor por línea, terminado en newline
3. **Ejemplo Arduino**:
```cpp
void loop() {
  int sensorValue = analogRead(A0);
  float voltage = sensorValue * (5.0 / 1023.0);
  Serial.println(voltage);
  delay(1);  // 1000 Hz
}
```

## 📝 Exportación de Datos

Los datos se pueden exportar en formato CSV con dos columnas:
- Tiempo (segundos)
- Amplitud (voltios)

```python
osc.export_data('datos.csv', use_filtered=False)
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork del repositorio
2. Crear una rama para tu feature
3. Commit de los cambios
4. Push a la rama
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y de investigación.

## 🔗 Referencias

- Procesamiento de señales con NumPy y SciPy
- Visualización con Matplotlib
- Comunicación serial con PySerial

## 👥 Autor

Proyecto desarrollado como sistema de osciloscopio digital para prototipado electrónico.
