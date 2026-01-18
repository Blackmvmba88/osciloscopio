"""
Módulo de persistencia digital y análisis avanzado de señales.
"""

import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from scipy import signal as scipy_signal


class DigitalPersistence:
    """
    Sistema de persistencia digital para análisis de jitter y variaciones estadísticas.
    """
    
    def __init__(self, width: int = 1000, height: int = 500, 
                 sample_rate: float = 1000.0):
        """
        Inicializa el sistema de persistencia.
        
        Args:
            width: Ancho del buffer de persistencia (muestras)
            height: Altura del buffer (niveles de amplitud)
            sample_rate: Frecuencia de muestreo
        """
        self.width = width
        self.height = height
        self.sample_rate = sample_rate
        
        # Buffer de persistencia (2D: tiempo x amplitud)
        self.persistence_buffer = np.zeros((height, width), dtype=np.float32)
        
        # Configuración
        self.decay_rate = 0.95  # Factor de decaimiento por frame
        self.color_temperature = 1.0  # Temperatura de color
        
        # Estadísticas
        self.num_captures = 0
        self.min_value = 0.0
        self.max_value = 1.0
    
    def set_range(self, min_val: float, max_val: float):
        """
        Establece el rango de valores de la señal.
        
        Args:
            min_val: Valor mínimo
            max_val: Valor máximo
        """
        self.min_value = min_val
        self.max_value = max_val
    
    def add_trace(self, data: np.ndarray, decay: bool = True):
        """
        Añade una traza al buffer de persistencia.
        
        Args:
            data: Datos de la señal
            decay: Si True, aplica decaimiento a trazas anteriores
        """
        if decay:
            self.persistence_buffer *= self.decay_rate
        
        # Redimensionar datos para ajustar al ancho del buffer
        if len(data) != self.width:
            indices = np.linspace(0, len(data) - 1, self.width).astype(int)
            data_resampled = data[indices]
        else:
            data_resampled = data
        
        # Normalizar al rango del buffer
        data_normalized = (data_resampled - self.min_value) / (self.max_value - self.min_value)
        data_normalized = np.clip(data_normalized, 0, 1)
        
        # Convertir a índices de fila
        row_indices = (data_normalized * (self.height - 1)).astype(int)
        col_indices = np.arange(self.width)
        
        # Incrementar contador de persistencia
        self.persistence_buffer[row_indices, col_indices] += 1.0
        
        self.num_captures += 1
    
    def get_persistence_map(self, normalize: bool = True) -> np.ndarray:
        """
        Obtiene el mapa de persistencia actual.
        
        Args:
            normalize: Si True, normaliza los valores al rango [0, 1]
            
        Returns:
            Mapa de persistencia (height x width)
        """
        if normalize and np.max(self.persistence_buffer) > 0:
            return self.persistence_buffer / np.max(self.persistence_buffer)
        return self.persistence_buffer.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calcula estadísticas del buffer de persistencia.
        
        Returns:
            Diccionario con estadísticas
        """
        # Calcular histograma vertical (distribución de amplitud)
        amplitude_histogram = np.sum(self.persistence_buffer, axis=1)
        
        # Calcular histograma horizontal (distribución temporal)
        time_histogram = np.sum(self.persistence_buffer, axis=0)
        
        # Índices de máxima actividad
        max_amplitude_idx = np.argmax(amplitude_histogram)
        max_time_idx = np.argmax(time_histogram)
        
        # Convertir índices a valores reales
        amplitude_at_max = self.min_value + (max_amplitude_idx / self.height) * (self.max_value - self.min_value)
        
        return {
            'num_captures': self.num_captures,
            'total_hits': int(np.sum(self.persistence_buffer)),
            'max_hits': int(np.max(self.persistence_buffer)),
            'mean_hits': float(np.mean(self.persistence_buffer[self.persistence_buffer > 0])) if np.any(self.persistence_buffer > 0) else 0.0,
            'most_common_amplitude': float(amplitude_at_max),
            'amplitude_histogram': amplitude_histogram,
            'time_histogram': time_histogram,
        }
    
    def reset(self):
        """Resetea el buffer de persistencia."""
        self.persistence_buffer.fill(0)
        self.num_captures = 0
    
    def set_decay_rate(self, rate: float):
        """
        Establece la tasa de decaimiento.
        
        Args:
            rate: Tasa de decaimiento (0-1), 1=sin decaimiento, 0=decaimiento total
        """
        self.decay_rate = np.clip(rate, 0.0, 1.0)


class AdvancedSpectralAnalysis:
    """
    Análisis espectral avanzado: STFT, wavelets, y métodos configurables.
    """
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa el analizador espectral avanzado.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
    
    def stft(self, data: np.ndarray, window_size: int = 256, 
             overlap: int = 128, window_type: str = 'hann') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula el Short-Time Fourier Transform.
        
        Args:
            data: Señal de entrada
            window_size: Tamaño de la ventana
            overlap: Solapamiento entre ventanas
            window_type: Tipo de ventana ('hann', 'hamming', 'blackman', etc.)
            
        Returns:
            Tupla (frecuencias, tiempos, espectrograma)
        """
        f, t, Zxx = scipy_signal.stft(
            data, 
            fs=self.sample_rate,
            window=window_type,
            nperseg=window_size,
            noverlap=overlap
        )
        
        return f, t, np.abs(Zxx)
    
    def welch_psd(self, data: np.ndarray, window_size: int = 256,
                  overlap: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula la densidad espectral de potencia usando el método de Welch.
        
        Args:
            data: Señal de entrada
            window_size: Tamaño de la ventana
            overlap: Solapamiento (por defecto 50% del tamaño de ventana)
            
        Returns:
            Tupla (frecuencias, PSD)
        """
        if overlap is None:
            overlap = window_size // 2
        
        f, psd = scipy_signal.welch(
            data,
            fs=self.sample_rate,
            nperseg=window_size,
            noverlap=overlap
        )
        
        return f, psd
    
    def spectrogram(self, data: np.ndarray, window_size: int = 256,
                    overlap: int = 128) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula el espectrograma de la señal.
        
        Args:
            data: Señal de entrada
            window_size: Tamaño de la ventana
            overlap: Solapamiento entre ventanas
            
        Returns:
            Tupla (frecuencias, tiempos, espectrograma)
        """
        f, t, Sxx = scipy_signal.spectrogram(
            data,
            fs=self.sample_rate,
            nperseg=window_size,
            noverlap=overlap
        )
        
        return f, t, Sxx
    
    def estimate_instantaneous_frequency(self, data: np.ndarray) -> np.ndarray:
        """
        Estima la frecuencia instantánea usando la transformada de Hilbert.
        
        Args:
            data: Señal de entrada
            
        Returns:
            Array con frecuencias instantáneas
        """
        # Transformada de Hilbert
        analytic_signal = scipy_signal.hilbert(data)
        
        # Fase instantánea
        instantaneous_phase = np.unwrap(np.angle(analytic_signal))
        
        # Frecuencia instantánea (derivada de la fase)
        instantaneous_frequency = np.diff(instantaneous_phase) / (2.0 * np.pi) * self.sample_rate
        
        # Añadir un elemento para mantener el mismo tamaño
        instantaneous_frequency = np.append(instantaneous_frequency, instantaneous_frequency[-1])
        
        return instantaneous_frequency
    
    def wavelet_transform(self, data: np.ndarray, wavelet: str = 'morl',
                         scales: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula la transformada wavelet continua (CWT).
        
        Args:
            data: Señal de entrada
            wavelet: Tipo de wavelet ('morl', 'mexh', 'cgau5', etc.)
            scales: Escalas para la CWT (por defecto: auto)
            
        Returns:
            Tupla (coeficientes, frecuencias)
        """
        try:
            import pywt
        except ImportError:
            print("pywavelets no está instalado. Instale con: pip install pywavelets")
            return np.array([]), np.array([])
        
        if scales is None:
            # Escalas automáticas
            scales = np.arange(1, min(len(data)//10, 128))
        
        # Calcular CWT
        coefficients, frequencies = pywt.cwt(data, scales, wavelet, 1/self.sample_rate)
        
        return coefficients, frequencies
    
    def adaptive_filter(self, data: np.ndarray, reference: Optional[np.ndarray] = None,
                       filter_order: int = 32, mu: float = 0.01) -> np.ndarray:
        """
        Filtro adaptativo LMS (Least Mean Squares).
        
        Args:
            data: Señal de entrada
            reference: Señal de referencia (si None, usa versión retardada de data)
            filter_order: Orden del filtro
            mu: Paso de adaptación
            
        Returns:
            Señal filtrada
        """
        if reference is None:
            # Usar versión retardada como referencia
            reference = np.roll(data, 1)
            reference[0] = data[0]
        
        # Inicializar pesos
        weights = np.zeros(filter_order)
        filtered = np.zeros(len(data))
        
        # Buffer de entrada
        input_buffer = np.zeros(filter_order)
        
        for i in range(len(data)):
            # Actualizar buffer
            input_buffer = np.roll(input_buffer, 1)
            input_buffer[0] = data[i]
            
            # Calcular salida
            filtered[i] = np.dot(weights, input_buffer)
            
            # Calcular error
            error = reference[i] - filtered[i]
            
            # Actualizar pesos (LMS)
            weights += mu * error * input_buffer
        
        return filtered
    
    def compute_coherence(self, signal1: np.ndarray, signal2: np.ndarray,
                         window_size: int = 256) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula la coherencia entre dos señales.
        
        Args:
            signal1: Primera señal
            signal2: Segunda señal
            window_size: Tamaño de la ventana
            
        Returns:
            Tupla (frecuencias, coherencia)
        """
        f, Cxy = scipy_signal.coherence(
            signal1, signal2,
            fs=self.sample_rate,
            nperseg=window_size
        )
        
        return f, Cxy
    
    def harmonic_analysis(self, data: np.ndarray, fundamental_freq: float,
                         num_harmonics: int = 10) -> Dict[str, Any]:
        """
        Análisis de armónicos de una señal.
        
        Args:
            data: Señal de entrada
            fundamental_freq: Frecuencia fundamental
            num_harmonics: Número de armónicos a analizar
            
        Returns:
            Diccionario con análisis de armónicos
        """
        # FFT
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(n, 1/self.sample_rate)
        fft_magnitude = np.abs(fft_vals)
        
        # Buscar armónicos
        harmonics = {}
        fundamental_amplitude = 0.0
        
        for h in range(1, num_harmonics + 1):
            target_freq = fundamental_freq * h
            
            # Buscar el pico más cercano a la frecuencia del armónico
            freq_window = 5.0  # Hz de tolerancia
            mask = np.abs(fft_freq - target_freq) < freq_window
            
            if np.any(mask):
                idx = np.argmax(fft_magnitude[mask])
                amplitude = fft_magnitude[mask][idx] / n * 2
                
                if h == 1:
                    fundamental_amplitude = amplitude
                
                harmonics[f'H{h}'] = {
                    'frequency': fft_freq[mask][idx],
                    'amplitude': float(amplitude),
                    'amplitude_db': float(20 * np.log10(amplitude + 1e-10)),
                    'relative_amplitude': float(amplitude / (fundamental_amplitude + 1e-10))
                }
        
        # Calcular THD
        thd = 0.0
        if fundamental_amplitude > 0:
            harmonic_sum = sum(
                harmonics[f'H{h}']['amplitude']**2 
                for h in range(2, num_harmonics + 1) 
                if f'H{h}' in harmonics
            )
            thd = np.sqrt(harmonic_sum) / fundamental_amplitude
        
        return {
            'fundamental_frequency': fundamental_freq,
            'fundamental_amplitude': float(fundamental_amplitude),
            'harmonics': harmonics,
            'thd': float(thd),
            'thd_db': float(20 * np.log10(thd + 1e-10)),
            'num_harmonics': len(harmonics),
        }


class CalibrationSystem:
    """
    Sistema de calibración para el osciloscopio.
    """
    
    def __init__(self):
        """Inicializa el sistema de calibración."""
        self.offset_calibration = 0.0
        self.gain_calibration = 1.0
        self.is_calibrated = False
        
        # Modelo de ruido
        self.thermal_noise_level = 0.0  # RMS
        self.shot_noise_level = 0.0
        self.flicker_noise_level = 0.0
    
    def calibrate_offset(self, ground_measurement: np.ndarray):
        """
        Calibra el offset usando una medición de tierra.
        
        Args:
            ground_measurement: Medición con entrada en tierra
        """
        self.offset_calibration = np.mean(ground_measurement)
        print(f"Offset calibrado: {self.offset_calibration:.6f} V")
    
    def calibrate_gain(self, known_signal: np.ndarray, known_amplitude: float):
        """
        Calibra la ganancia usando una señal de amplitud conocida.
        
        Args:
            known_signal: Señal de amplitud conocida
            known_amplitude: Amplitud real de la señal
        """
        measured_amplitude = np.max(known_signal) - np.min(known_signal)
        self.gain_calibration = known_amplitude / measured_amplitude
        self.is_calibrated = True
        print(f"Ganancia calibrada: {self.gain_calibration:.6f}")
    
    def apply_calibration(self, data: np.ndarray) -> np.ndarray:
        """
        Aplica la calibración a los datos.
        
        Args:
            data: Datos sin calibrar
            
        Returns:
            Datos calibrados
        """
        # Aplicar offset y ganancia
        calibrated = (data - self.offset_calibration) * self.gain_calibration
        return calibrated
    
    def add_noise_model(self, data: np.ndarray, 
                       thermal: bool = True,
                       shot: bool = True,
                       flicker: bool = True) -> np.ndarray:
        """
        Añade modelo de ruido a los datos.
        
        Args:
            data: Datos limpios
            thermal: Añadir ruido térmico
            shot: Añadir ruido shot
            flicker: Añadir ruido flicker (1/f)
            
        Returns:
            Datos con ruido modelado
        """
        noisy_data = data.copy()
        n = len(data)
        
        # Ruido térmico (Gaussiano blanco)
        if thermal and self.thermal_noise_level > 0:
            thermal_noise = np.random.normal(0, self.thermal_noise_level, n)
            noisy_data += thermal_noise
        
        # Ruido shot (Poisson)
        if shot and self.shot_noise_level > 0:
            # Aproximación: ruido Gaussiano proporcional a sqrt(señal)
            shot_noise = np.random.normal(0, self.shot_noise_level, n) * np.sqrt(np.abs(data) + 1e-10)
            noisy_data += shot_noise
        
        # Ruido flicker (1/f)
        if flicker and self.flicker_noise_level > 0:
            # Generar ruido 1/f en dominio de frecuencia
            fft_noise = np.fft.fft(np.random.randn(n))
            freqs = np.fft.fftfreq(n)
            freqs[0] = 1e-10  # Evitar división por cero
            fft_noise = fft_noise / np.sqrt(np.abs(freqs))
            flicker_noise = np.real(np.fft.ifft(fft_noise))
            flicker_noise = flicker_noise / np.std(flicker_noise) * self.flicker_noise_level
            noisy_data += flicker_noise
        
        return noisy_data
    
    def set_noise_levels(self, thermal: float = 0.01, 
                        shot: float = 0.005,
                        flicker: float = 0.002):
        """
        Configura los niveles de ruido del modelo.
        
        Args:
            thermal: Nivel de ruido térmico (RMS)
            shot: Nivel de ruido shot
            flicker: Nivel de ruido flicker
        """
        self.thermal_noise_level = thermal
        self.shot_noise_level = shot
        self.flicker_noise_level = flicker
    
    def get_calibration_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de calibración.
        
        Returns:
            Diccionario con estado de calibración
        """
        return {
            'is_calibrated': self.is_calibrated,
            'offset': self.offset_calibration,
            'gain': self.gain_calibration,
            'thermal_noise': self.thermal_noise_level,
            'shot_noise': self.shot_noise_level,
            'flicker_noise': self.flicker_noise_level,
        }
