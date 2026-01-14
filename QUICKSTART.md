# Guía de Inicio Rápido - Osciloscopio Digital

## Instalación Rápida

```bash
git clone https://github.com/Blackmvmba88/osciloscopio.git
cd osciloscopio
pip install -r requirements.txt
pip install -e .
```

## Ejemplo de 5 Minutos

```python
from osciloscopio import DigitalOscilloscope, FilterType

# 1. Crear osciloscopio
osc = DigitalOscilloscope(sample_rate=1000.0, source_type='simulated')

# 2. Iniciar y capturar
osc.start()
data = osc.capture(duration=2.0)

# 3. Analizar
osc.print_analysis()

# 4. Filtrar
osc.apply_filter(FilterType.LOWPASS, cutoff=50.0)

# 5. Visualizar
osc.plot_signal()
osc.plot_fft()
osc.create_dashboard()

# 6. Exportar
osc.export_data('mi_señal.csv')

osc.stop()
```

## Ejecutar Ejemplos

```bash
# Ejemplo básico
python examples/basic_example.py

# Ejemplos avanzados
python examples/advanced_example.py

# Demo completa
python demo_complete.py

# Suite de pruebas
python test_oscilloscope.py
```

## Características Principales

### ✅ Captura de Señales
- Hardware externo (puerto serial)
- Fuentes simuladas (sine, square, triangle, sawtooth, mixed)
- Configuración flexible de parámetros

### ✅ Procesamiento
- 6 tipos de filtros (Butterworth, media móvil, mediana)
- Eliminación DC, normalización, submuestreo
- Decodificación PWM

### ✅ Análisis
- 13+ métricas (RMS, pico-pico, frecuencia, SNR, THD)
- Análisis espectral (FFT)
- Mediciones temporales (rise/fall time)

### ✅ Visualización
- Gráficos temporales y espectrales
- Espectrogramas
- Dashboards multipanel
- Exportación en alta resolución

## Conectar Hardware

```python
# Configuración para Arduino u otro microcontrolador
osc = DigitalOscilloscope(sample_rate=1000.0, source_type='hardware')
osc.source.port = '/dev/ttyUSB0'  # Linux/Mac
# osc.source.port = 'COM3'  # Windows
osc.source.baudrate = 115200

osc.start()
osc.capture(duration=5.0)
```

### Código Arduino de Ejemplo

```cpp
void setup() {
  Serial.begin(115200);
}

void loop() {
  int sensorValue = analogRead(A0);
  float voltage = sensorValue * (5.0 / 1023.0);
  Serial.println(voltage);
  delay(1);  // 1000 Hz
}
```

## Preguntas Frecuentes

**P: ¿Qué frecuencia de muestreo debo usar?**
R: Mínimo 2x la frecuencia máxima de tu señal (teorema de Nyquist). Para 50 Hz, usa ≥100 Hz.

**P: ¿Puedo analizar señales reales de sensores?**
R: Sí, conecta tu sensor a Arduino/ESP32 y envía los valores por serial.

**P: ¿Funciona en Windows/Mac/Linux?**
R: Sí, es multiplataforma (Python 3.8+).

**P: ¿Necesito hardware especial?**
R: No, puedes usar el modo simulado para aprender y prototipar.

## Soporte y Contribuciones

- 📖 Documentación completa en [README.md](README.md)
- 🐛 Reportar problemas en GitHub Issues
- 🤝 Pull requests bienvenidos

## Licencia

Código abierto para uso educativo y de investigación.
