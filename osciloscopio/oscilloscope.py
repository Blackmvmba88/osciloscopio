"""
Módulo principal del osciloscopio digital: orquestador de todos los componentes.
"""

import numpy as np
from typing import Optional, Dict, List
from .acquisition import SignalSource, HardwareSource, SimulatedSource
from .processing import SignalProcessor, FilterType
from .visualization import SignalVisualizer
from .analyzer import SignalAnalyzer


class DigitalOscilloscope:
    """
    Osciloscopio digital completo que integra todos los módulos.
    """
    
    def __init__(self, sample_rate: float = 1000.0, 
                 source_type: str = 'simulated'):
        """
        Inicializa el osciloscopio digital.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
            source_type: Tipo de fuente ('hardware' o 'simulated')
        """
        self.sample_rate = sample_rate
        
        # Inicializa los módulos
        self.processor = SignalProcessor(sample_rate)
        self.visualizer = SignalVisualizer(sample_rate)
        self.analyzer = SignalAnalyzer(sample_rate)
        
        # Inicializa la fuente de señales
        if source_type == 'hardware':
            self.source = HardwareSource(sample_rate=sample_rate)
        else:
            self.source = SimulatedSource(sample_rate=sample_rate)
        
        # Buffer de datos
        self.raw_data: Optional[np.ndarray] = None
        self.processed_data: Optional[np.ndarray] = None
        
        print(f"Osciloscopio Digital inicializado")
        print(f"Frecuencia de muestreo: {sample_rate} Hz")
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
