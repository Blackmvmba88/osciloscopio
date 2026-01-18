"""
Módulo principal del osciloscopio digital: orquestador de todos los componentes.
"""

import numpy as np
from typing import Optional, Dict, List, Any
from .acquisition import SignalSource, HardwareSource, SimulatedSource
from .processing import SignalProcessor, FilterType
from .visualization import SignalVisualizer
from .analyzer import SignalAnalyzer
from .trigger import TriggerSystem, TriggerType, TriggerMode
from .multichannel import MultiChannelManager
from .protocols import ProtocolDecoder


class DigitalOscilloscope:
    """
    Osciloscopio digital completo que integra todos los módulos.
    """
    
    def __init__(self, sample_rate: float = 1000.0, 
                 source_type: str = 'simulated',
                 num_channels: int = 1):
        """
        Inicializa el osciloscopio digital.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
            source_type: Tipo de fuente ('hardware' o 'simulated')
            num_channels: Número de canales (1-8)
        """
        self.sample_rate = sample_rate
        self.num_channels = num_channels
        
        # Inicializa los módulos
        self.processor = SignalProcessor(sample_rate)
        self.visualizer = SignalVisualizer(sample_rate)
        self.analyzer = SignalAnalyzer(sample_rate)
        
        # Nuevos módulos avanzados
        self.trigger = TriggerSystem(sample_rate)
        self.channels = MultiChannelManager(num_channels, sample_rate)
        self.protocol_decoder = ProtocolDecoder(sample_rate)
        
        # Inicializa la fuente de señales
        if source_type == 'hardware':
            self.source = HardwareSource(sample_rate=sample_rate)
        else:
            self.source = SimulatedSource(sample_rate=sample_rate)
        
        # Buffer de datos (mantener compatibilidad con código existente)
        self.raw_data: Optional[np.ndarray] = None
        self.processed_data: Optional[np.ndarray] = None
        
        print(f"Osciloscopio Digital inicializado")
        print(f"Frecuencia de muestreo: {sample_rate} Hz")
        print(f"Canales: {num_channels}")
        print(f"Fuente: {source_type}")
    
    def start(self):
        """Inicia la captura de señales."""
        self.source.start()
        print("Captura de señales iniciada")
    
    def stop(self):
        """Detiene la captura de señales."""
        self.source.stop()
        print("Captura de señales detenida")
    
    def capture(self, duration: float = 1.0) -> np.ndarray:
        """
        Captura una ventana de datos.
        
        Args:
            duration: Duración de la captura en segundos
            
        Returns:
            Array con los datos capturados
        """
        num_samples = int(duration * self.sample_rate)
        
        if not self.source.is_running():
            self.start()
        
        print(f"Capturando {num_samples} muestras ({duration} segundos)...")
        self.raw_data = self.source.read_samples(num_samples)
        print(f"Captura completada: {len(self.raw_data)} muestras")
        
        return self.raw_data
    
    def apply_filter(self, filter_type: FilterType, **kwargs) -> np.ndarray:
        """
        Aplica un filtro a los datos capturados.
        
        Args:
            filter_type: Tipo de filtro
            **kwargs: Parámetros del filtro
            
        Returns:
            Datos filtrados
        """
        if self.raw_data is None:
            print("No hay datos capturados. Ejecute capture() primero.")
            return np.array([])
        
        print(f"Aplicando filtro: {filter_type.value}")
        self.processed_data = self.processor.apply_filter(
            self.raw_data, filter_type, **kwargs
        )
        print("Filtro aplicado")
        
        return self.processed_data
    
    def analyze(self, use_filtered: bool = False) -> Dict:
        """
        Analiza la señal capturada.
        
        Args:
            use_filtered: Si True, analiza datos filtrados; si False, datos crudos
            
        Returns:
            Diccionario con resultados del análisis
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
            print("Analizando señal filtrada...")
        elif self.raw_data is not None:
            data = self.raw_data
            print("Analizando señal cruda...")
        else:
            print("No hay datos para analizar. Ejecute capture() primero.")
            return {}
        
        results = self.analyzer.analyze(data)
        return results
    
    def print_analysis(self, use_filtered: bool = False):
        """
        Imprime el análisis de la señal.
        
        Args:
            use_filtered: Si True, analiza datos filtrados; si False, datos crudos
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
        elif self.raw_data is not None:
            data = self.raw_data
        else:
            print("No hay datos para analizar. Ejecute capture() primero.")
            return
        
        self.analyzer.print_analysis(data)
    
    def plot_signal(self, use_filtered: bool = False, 
                   save_path: Optional[str] = None):
        """
        Visualiza la señal capturada.
        
        Args:
            use_filtered: Si True, muestra datos filtrados; si False, datos crudos
            save_path: Ruta para guardar la figura
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
            title = "Señal Filtrada"
        elif self.raw_data is not None:
            data = self.raw_data
            title = "Señal Capturada"
        else:
            print("No hay datos para visualizar. Ejecute capture() primero.")
            return
        
        self.visualizer.plot_signal(data, title=title, save_path=save_path)
    
    def plot_comparison(self, save_path: Optional[str] = None):
        """
        Visualiza la comparación entre señal cruda y filtrada.
        
        Args:
            save_path: Ruta para guardar la figura
        """
        if self.raw_data is None:
            print("No hay datos para visualizar. Ejecute capture() primero.")
            return
        
        if self.processed_data is None:
            print("No hay datos filtrados. Ejecute apply_filter() primero.")
            return
        
        self.visualizer.plot_multiple_signals(
            [self.raw_data, self.processed_data],
            ["Señal Original", "Señal Filtrada"],
            title="Comparación: Original vs Filtrada",
            save_path=save_path
        )
    
    def plot_fft(self, use_filtered: bool = False, 
                max_freq: Optional[float] = None,
                save_path: Optional[str] = None):
        """
        Visualiza el espectro de frecuencia.
        
        Args:
            use_filtered: Si True, muestra FFT de datos filtrados
            max_freq: Frecuencia máxima a mostrar
            save_path: Ruta para guardar la figura
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
            title = "Espectro de Frecuencia (Filtrada)"
        elif self.raw_data is not None:
            data = self.raw_data
            title = "Espectro de Frecuencia (Original)"
        else:
            print("No hay datos para visualizar. Ejecute capture() primero.")
            return
        
        self.visualizer.plot_fft(data, title=title, max_freq=max_freq,
                                save_path=save_path)
    
    def plot_spectrogram(self, use_filtered: bool = False,
                        save_path: Optional[str] = None):
        """
        Visualiza el espectrograma.
        
        Args:
            use_filtered: Si True, muestra espectrograma de datos filtrados
            save_path: Ruta para guardar la figura
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
            title = "Espectrograma (Filtrada)"
        elif self.raw_data is not None:
            data = self.raw_data
            title = "Espectrograma (Original)"
        else:
            print("No hay datos para visualizar. Ejecute capture() primero.")
            return
        
        self.visualizer.plot_spectrogram(data, title=title, 
                                        save_path=save_path)
    
    def create_dashboard(self, save_path: Optional[str] = None):
        """
        Crea un dashboard completo con múltiples visualizaciones.
        
        Args:
            save_path: Ruta para guardar la figura
        """
        if self.raw_data is None:
            print("No hay datos para visualizar. Ejecute capture() primero.")
            return
        
        if self.processed_data is None:
            # Si no hay datos filtrados, aplica un filtro paso bajo por defecto
            self.processed_data = self.processor.apply_filter(
                self.raw_data, FilterType.LOWPASS, cutoff=50.0
            )
        
        self.visualizer.create_dashboard(
            self.raw_data, self.processed_data,
            title="Dashboard de Análisis de Señal",
            save_path=save_path
        )
    
    def decode_pwm(self, threshold: Optional[float] = None) -> Dict:
        """
        Decodifica señales PWM.
        
        Args:
            threshold: Umbral de detección
            
        Returns:
            Diccionario con información PWM
        """
        if self.raw_data is None:
            print("No hay datos para decodificar. Ejecute capture() primero.")
            return {}
        
        print("Decodificando señal PWM...")
        pwm_info = self.processor.decode_pwm(self.raw_data, threshold)
        
        print(f"Ciclo de trabajo: {pwm_info['duty_cycle']:.2f}%")
        print(f"Frecuencia: {pwm_info['frequency']:.2f} Hz")
        print(f"Período: {pwm_info['period']*1000:.2f} ms")
        
        return pwm_info
    
    def export_data(self, filename: str, use_filtered: bool = False):
        """
        Exporta los datos a un archivo CSV.
        
        Args:
            filename: Nombre del archivo de salida
            use_filtered: Si True, exporta datos filtrados
        """
        if use_filtered and self.processed_data is not None:
            data = self.processed_data
        elif self.raw_data is not None:
            data = self.raw_data
        else:
            print("No hay datos para exportar. Ejecute capture() primero.")
            return
        
        t = np.arange(len(data)) / self.sample_rate
        
        # Save in CSV format
        np.savetxt(filename, np.column_stack((t, data)),
                  delimiter=',', header='Time(s),Amplitude(V)',
                  comments='')
        
        print(f"Datos exportados a: {filename}")
    
    def set_source_parameters(self, **kwargs):
        """
        Configura los parámetros de la fuente de señales.
        
        Args:
            **kwargs: Parámetros a configurar
        """
        if isinstance(self.source, SimulatedSource):
            self.source.set_parameters(**kwargs)
            print("Parámetros de la fuente actualizados")
        else:
            print("Esta función solo está disponible para fuentes simuladas")
    
    # ===== NUEVOS MÉTODOS AVANZADOS =====
    
    def configure_trigger(self, **kwargs):
        """
        Configura el sistema de triggers.
        
        Args:
            **kwargs: Parámetros de trigger (ver TriggerConfig)
                trigger_type: 'rising_edge', 'falling_edge', 'pulse_width', etc.
                level: Nivel de trigger
                mode: 'auto', 'normal', 'single'
        
        Example:
            osc.configure_trigger(
                trigger_type='rising_edge',
                level=0.5,
                mode='normal',
                hysteresis=0.1
            )
        """
        self.trigger.configure(**kwargs)
        print(f"Trigger configurado: {self.trigger.get_status()}")
    
    def capture_with_trigger(self, duration: float = 1.0, 
                            pre_trigger_percent: float = 10.0) -> np.ndarray:
        """
        Captura datos con sistema de trigger.
        
        Args:
            duration: Duración de la captura en segundos
            pre_trigger_percent: Porcentaje de datos antes del trigger
            
        Returns:
            Datos capturados con trigger aplicado
        """
        # Capturar datos normalmente
        data = self.capture(duration)
        
        # Aplicar trigger
        triggered_data, trigger_idx = self.trigger.apply_trigger(
            data, pre_trigger_percent
        )
        
        if trigger_idx is not None:
            print(f"Trigger encontrado en índice: {trigger_idx}")
        else:
            print("Trigger no encontrado (modo auto activo)")
        
        self.raw_data = triggered_data
        return triggered_data
    
    def configure_channel(self, channel: int, **kwargs):
        """
        Configura un canal específico.
        
        Args:
            channel: Número de canal (0-based)
            **kwargs: Parámetros del canal (ver ChannelConfig)
        
        Example:
            osc.configure_channel(0, 
                enabled=True,
                vertical_scale=1.0,
                coupling='dc',
                label='Voltage'
            )
        """
        self.channels.configure_channel(channel, **kwargs)
        print(f"Canal {channel} configurado")
    
    def capture_channel(self, channel: int, duration: float = 1.0) -> np.ndarray:
        """
        Captura datos de un canal específico.
        
        Args:
            channel: Número de canal
            duration: Duración en segundos
            
        Returns:
            Datos del canal
        """
        data = self.capture(duration)
        self.channels.set_channel_data(channel, data)
        
        # Actualizar buffer principal para compatibilidad
        if channel == 0:
            self.raw_data = data
        
        return data
    
    def measure(self, metric: str, channel: int = 0, 
                use_filtered: bool = False) -> float:
        """
        Realiza una medición específica en un canal.
        
        Args:
            metric: Métrica a medir ('frequency', 'rms', 'thd', 'snr', etc.)
            channel: Número de canal
            use_filtered: Usar datos filtrados
            
        Returns:
            Valor de la métrica
            
        Example:
            freq = osc.measure('frequency', channel=0)
            rms = osc.measure('rms', channel=1)
        """
        # Obtener datos del canal
        data = self.channels.get_channel_data(channel)
        
        if data is None:
            # Fallback a buffer principal
            if use_filtered and self.processed_data is not None:
                data = self.processed_data
            elif self.raw_data is not None:
                data = self.raw_data
            else:
                print(f"No hay datos en canal {channel}")
                return 0.0
        
        # Realizar análisis
        results = self.analyzer.analyze(data)
        
        # Retornar métrica específica
        if metric in results:
            return results[metric]
        else:
            print(f"Métrica '{metric}' no disponible. Métricas: {list(results.keys())}")
            return 0.0
    
    def cross_channel_analysis(self, channel_a: int, channel_b: int) -> Dict[str, Any]:
        """
        Análisis cruzado entre dos canales.
        
        Args:
            channel_a: Primer canal
            channel_b: Segundo canal
            
        Returns:
            Diccionario con análisis cruzado
            
        Example:
            result = osc.cross_channel_analysis(0, 1)
            print(f"Diferencia de fase: {result['phase_difference_deg']}°")
        """
        return self.channels.cross_channel_analysis(channel_a, channel_b)
    
    def decode_uart(self, channel: int = 0, baud_rate: int = 9600, 
                    **kwargs) -> List:
        """
        Decodifica protocolo UART en un canal.
        
        Args:
            channel: Canal con datos UART
            baud_rate: Velocidad en baudios
            **kwargs: Parámetros adicionales (data_bits, parity, stop_bits)
            
        Returns:
            Lista de frames UART decodificados
            
        Example:
            frames = osc.decode_uart(0, baud_rate=9600, data_bits=8)
            text = osc.protocol_decoder.uart_decoder.frames_to_string(frames)
        """
        data = self.channels.get_channel_data(channel)
        if data is None:
            data = self.raw_data
        
        if data is None:
            print(f"No hay datos en canal {channel}")
            return []
        
        frames = self.protocol_decoder.decode_uart(
            data, baud_rate=baud_rate, **kwargs
        )
        print(f"UART: {len(frames)} frames decodificados")
        return frames
    
    def decode_i2c(self, scl_channel: int = 0, sda_channel: int = 1, 
                   **kwargs) -> List:
        """
        Decodifica protocolo I2C.
        
        Args:
            scl_channel: Canal con señal SCL (reloj)
            sda_channel: Canal con señal SDA (datos)
            **kwargs: Parámetros adicionales
            
        Returns:
            Lista de transacciones I2C
            
        Example:
            transactions = osc.decode_i2c(scl_channel=0, sda_channel=1)
        """
        scl = self.channels.get_channel_data(scl_channel)
        sda = self.channels.get_channel_data(sda_channel)
        
        if scl is None or sda is None:
            print("Necesita datos en ambos canales (SCL y SDA)")
            return []
        
        transactions = self.protocol_decoder.decode_i2c(scl, sda, **kwargs)
        print(f"I2C: {len(transactions)} transacciones decodificadas")
        return transactions
    
    def decode_spi(self, sclk_channel: int = 0, mosi_channel: int = 1,
                   miso_channel: int = 2, cs_channel: Optional[int] = None,
                   **kwargs) -> List:
        """
        Decodifica protocolo SPI.
        
        Args:
            sclk_channel: Canal con señal de reloj
            mosi_channel: Canal MOSI
            miso_channel: Canal MISO
            cs_channel: Canal Chip Select (opcional)
            **kwargs: Parámetros adicionales (mode, bit_order, bits_per_word)
            
        Returns:
            Lista de transacciones SPI
            
        Example:
            transactions = osc.decode_spi(0, 1, 2, mode=0)
        """
        sclk = self.channels.get_channel_data(sclk_channel)
        mosi = self.channels.get_channel_data(mosi_channel)
        miso = self.channels.get_channel_data(miso_channel)
        
        cs = None
        if cs_channel is not None:
            cs = self.channels.get_channel_data(cs_channel)
        
        if sclk is None or mosi is None or miso is None:
            print("Necesita datos en canales SCLK, MOSI y MISO")
            return []
        
        transactions = self.protocol_decoder.decode_spi(
            sclk, mosi, miso, cs, **kwargs
        )
        print(f"SPI: {len(transactions)} transacciones decodificadas")
        return transactions
    
    def get_channel_info(self, channel: Optional[int] = None) -> Any:
        """
        Obtiene información de un canal o todos los canales.
        
        Args:
            channel: Número de canal o None para todos
            
        Returns:
            Información del canal o lista de todos los canales
        """
        if channel is not None:
            return self.channels.get_channel_info(channel)
        else:
            return self.channels.get_all_channels_info()
    
    def export_wav(self, filename: str, channel: int = 0, 
                   use_filtered: bool = False):
        """
        Exporta datos a formato WAV.
        
        Args:
            filename: Nombre del archivo (debe terminar en .wav)
            channel: Canal a exportar
            use_filtered: Usar datos filtrados
        """
        try:
            from scipy.io import wavfile
        except ImportError:
            print("scipy no está disponible para exportar WAV")
            return
        
        # Obtener datos
        data = self.channels.get_channel_data(channel)
        if data is None:
            if use_filtered and self.processed_data is not None:
                data = self.processed_data
            elif self.raw_data is not None:
                data = self.raw_data
            else:
                print("No hay datos para exportar")
                return
        
        # Normalizar a rango de 16-bit integer
        data_normalized = np.int16(data / np.max(np.abs(data)) * 32767)
        
        # Guardar
        wavfile.write(filename, int(self.sample_rate), data_normalized)
        print(f"Datos exportados a WAV: {filename}")
    
    def export_npy(self, filename: str, channel: int = 0,
                   use_filtered: bool = False):
        """
        Exporta datos a formato NumPy (.npy).
        
        Args:
            filename: Nombre del archivo
            channel: Canal a exportar
            use_filtered: Usar datos filtrados
        """
        data = self.channels.get_channel_data(channel)
        if data is None:
            if use_filtered and self.processed_data is not None:
                data = self.processed_data
            elif self.raw_data is not None:
                data = self.raw_data
            else:
                print("No hay datos para exportar")
                return
        
        np.save(filename, data)
        print(f"Datos exportados a NPY: {filename}")
    
    def export_matlab(self, filename: str, channel: int = 0,
                      use_filtered: bool = False):
        """
        Exporta datos a formato MATLAB (.mat).
        
        Args:
            filename: Nombre del archivo
            channel: Canal a exportar
            use_filtered: Usar datos filtrados
        """
        try:
            from scipy.io import savemat
        except ImportError:
            print("scipy no está disponible para exportar MAT")
            return
        
        data = self.channels.get_channel_data(channel)
        if data is None:
            if use_filtered and self.processed_data is not None:
                data = self.processed_data
            elif self.raw_data is not None:
                data = self.raw_data
            else:
                print("No hay datos para exportar")
                return
        
        # Crear diccionario con metadata
        mat_data = {
            'signal': data,
            'sample_rate': self.sample_rate,
            'channel': channel,
            'num_samples': len(data),
        }
        
        savemat(filename, mat_data)
        print(f"Datos exportados a MATLAB: {filename}")
