# Osciloscopio Digital 📊

Sistema de osciloscopio digital orientado a prototipado electrónico: captura, decodifica y analiza señales en hardware externo o fuentes simuladas. Visualización interactiva, filtros configurables y módulos de análisis.

## 🎯 Características

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

### Ejemplo 1: Análisis de Señales Simuladas

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

### Ejemplo 2: Captura desde Hardware

```python
from osciloscopio import DigitalOscilloscope, FilterType

# Conectar con hardware
osc = DigitalOscilloscope(sample_rate=1000.0, source_type='hardware')

# Configurar puerto (opcional)
osc.source.port = '/dev/ttyUSB0'  # Linux
# osc.source.port = 'COM3'  # Windows
osc.source.baudrate = 115200

osc.start()
osc.capture(duration=5.0)

# Filtrar ruido
osc.apply_filter(FilterType.LOWPASS, cutoff=100.0)

# Comparar original vs filtrada
osc.plot_comparison(save_path='comparison.png')
```

### Ejemplo 3: Decodificación PWM

```python
from osciloscopio import DigitalOscilloscope

osc = DigitalOscilloscope(sample_rate=10000.0, source_type='simulated')
osc.source.signal_type = 'square'
osc.source.frequency = 1000.0

osc.start()
osc.capture(duration=0.1)

# Decodificar PWM
pwm_info = osc.decode_pwm()
print(f"Ciclo de trabajo: {pwm_info['duty_cycle']:.2f}%")
print(f"Frecuencia: {pwm_info['frequency']:.2f} Hz")
```

### Ejemplo 4: Dashboard Completo

```python
from osciloscopio import DigitalOscilloscope, FilterType

osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')
osc.source.signal_type = 'mixed'

osc.start()
osc.capture(duration=3.0)
osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)

# Crear dashboard con 4 vistas
osc.create_dashboard(save_path='dashboard.png')
```

## 📁 Estructura del Proyecto

```
osciloscopio/
├── osciloscopio/
│   ├── __init__.py          # Inicialización del paquete
│   ├── acquisition.py       # Captura de señales (hardware/simulado)
│   ├── processing.py        # Filtros y procesamiento
│   ├── visualization.py     # Visualización interactiva
│   ├── analyzer.py          # Análisis y mediciones
│   └── oscilloscope.py      # Clase principal (orquestador)
├── examples/
│   ├── basic_example.py     # Ejemplo básico
│   ├── advanced_example.py  # Ejemplos avanzados
│   └── hardware_example.py  # Captura desde hardware
├── requirements.txt         # Dependencias
├── setup.py                 # Configuración del paquete
└── README.md               # Documentación
```

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
- Estadísticas básicas
- Análisis de frecuencia
- Mediciones temporales
- Calidad de señal (SNR, THD)
- Detección de picos

### oscilloscope.py
Clase principal que integra todos los módulos y proporciona una interfaz unificada.

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
