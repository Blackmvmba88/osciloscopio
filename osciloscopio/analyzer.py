"""
Módulo de análisis de señales: mediciones y estadísticas.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional


class SignalAnalyzer:
    """Analizador de señales con múltiples métricas."""
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa el analizador.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
    
    def analyze(self, data: np.ndarray) -> Dict[str, float]:
        """
        Realiza un análisis completo de la señal.
        
        Args:
            data: Datos de entrada
            
        Returns:
            Diccionario con todas las métricas calculadas
        """
        return {
            'mean': self.calculate_mean(data),
            'rms': self.calculate_rms(data),
            'peak_to_peak': self.calculate_peak_to_peak(data),
            'min': self.calculate_min(data),
            'max': self.calculate_max(data),
            'std': self.calculate_std(data),
            'variance': self.calculate_variance(data),
            'frequency': self.estimate_frequency(data),
            'period': self.estimate_period(data),
            'duty_cycle': self.estimate_duty_cycle(data),
            'rise_time': self.calculate_rise_time(data),
            'fall_time': self.calculate_fall_time(data),
            'snr': self.calculate_snr(data),
        }
    
    def calculate_mean(self, data: np.ndarray) -> float:
        """Calcula el valor medio de la señal."""
        return float(np.mean(data))
    
    def calculate_rms(self, data: np.ndarray) -> float:
        """Calcula el valor RMS (Root Mean Square) de la señal."""
        return float(np.sqrt(np.mean(data**2)))
    
    def calculate_peak_to_peak(self, data: np.ndarray) -> float:
        """Calcula la amplitud pico a pico."""
        return float(np.max(data) - np.min(data))
    
    def calculate_min(self, data: np.ndarray) -> float:
        """Calcula el valor mínimo de la señal."""
        return float(np.min(data))
    
    def calculate_max(self, data: np.ndarray) -> float:
        """Calcula el valor máximo de la señal."""
        return float(np.max(data))
    
    def calculate_std(self, data: np.ndarray) -> float:
        """Calcula la desviación estándar."""
        return float(np.std(data))
    
    def calculate_variance(self, data: np.ndarray) -> float:
        """Calcula la varianza."""
        return float(np.var(data))
    
    def estimate_frequency(self, data: np.ndarray) -> float:
        """
        Estima la frecuencia fundamental de la señal usando FFT.
        
        Args:
            data: Datos de entrada
            
        Returns:
            Frecuencia en Hz
        """
        # FFT
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(n, 1/self.sample_rate)
        
        # Solo frecuencias positivas
        positive_idx = fft_freq > 0
        fft_freq = fft_freq[positive_idx]
        fft_magnitude = np.abs(fft_vals[positive_idx])
        
        # Encuentra el pico de frecuencia
        if len(fft_magnitude) > 0:
            peak_idx = np.argmax(fft_magnitude)
            fundamental_freq = fft_freq[peak_idx]
            return float(fundamental_freq)
        
        return 0.0
    
    def estimate_period(self, data: np.ndarray) -> float:
        """
        Estima el período de la señal.
        
        Args:
            data: Datos de entrada
            
        Returns:
            Período en segundos
        """
        freq = self.estimate_frequency(data)
        if freq > 0:
            return 1.0 / freq
        return 0.0
    
    def estimate_duty_cycle(self, data: np.ndarray, 
                           threshold: Optional[float] = None) -> float:
        """
        Estima el ciclo de trabajo para señales digitales.
        
        Args:
            data: Datos de entrada
            threshold: Umbral de detección (None = automático)
            
        Returns:
            Ciclo de trabajo en porcentaje (0-100)
        """
        if threshold is None:
            threshold = (np.max(data) + np.min(data)) / 2
        
        high_samples = np.sum(data > threshold)
        total_samples = len(data)
        
        if total_samples > 0:
            return float(100.0 * high_samples / total_samples)
        
        return 0.0
    
    def calculate_rise_time(self, data: np.ndarray,
                           low_threshold: float = 0.1,
                           high_threshold: float = 0.9) -> float:
        """
        Calcula el tiempo de subida (10% a 90%).
        
        Args:
            data: Datos de entrada
            low_threshold: Umbral inferior (fracción)
            high_threshold: Umbral superior (fracción)
            
        Returns:
            Tiempo de subida en segundos
        """
        # Normaliza los datos
        data_min = np.min(data)
        data_max = np.max(data)
        data_range = data_max - data_min
        
        if data_range == 0:
            return 0.0
        
        normalized = (data - data_min) / data_range
        
        # Encuentra cruces por umbral
        low_val = low_threshold
        high_val = high_threshold
        
        # Busca el primer cruce del umbral inferior
        low_cross = np.where(normalized > low_val)[0]
        high_cross = np.where(normalized > high_val)[0]
        
        if len(low_cross) > 0 and len(high_cross) > 0:
            rise_samples = high_cross[0] - low_cross[0]
            rise_time = rise_samples / self.sample_rate
            return float(rise_time)
        
        return 0.0
    
    def calculate_fall_time(self, data: np.ndarray,
                           low_threshold: float = 0.1,
                           high_threshold: float = 0.9) -> float:
        """
        Calcula el tiempo de bajada (90% a 10%).
        
        Args:
            data: Datos de entrada
            low_threshold: Umbral inferior (fracción)
            high_threshold: Umbral superior (fracción)
            
        Returns:
            Tiempo de bajada en segundos
        """
        # Normaliza los datos
        data_min = np.min(data)
        data_max = np.max(data)
        data_range = data_max - data_min
        
        if data_range == 0:
            return 0.0
        
        normalized = (data - data_min) / data_range
        
        # Busca transiciones de bajada
        high_val = high_threshold
        low_val = low_threshold
        
        # Encuentra donde está por encima del umbral alto
        high_regions = normalized > high_val
        # Encuentra donde está por debajo del umbral bajo
        low_regions = normalized < low_val
        
        # Busca transiciones
        for i in range(len(data) - 1):
            if high_regions[i] and not high_regions[i + 1]:
                # Encontró inicio de bajada
                for j in range(i + 1, len(data)):
                    if low_regions[j]:
                        fall_samples = j - i
                        fall_time = fall_samples / self.sample_rate
                        return float(fall_time)
        
        return 0.0
    
    def calculate_snr(self, data: np.ndarray) -> float:
        """
        Calcula la relación señal a ruido (SNR) en dB.
        
        Args:
            data: Datos de entrada
            
        Returns:
            SNR en dB
        """
        # Asume que la señal es periódica
        # Estima la potencia de la señal usando FFT
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_magnitude = np.abs(fft_vals)
        
        # Encuentra los picos principales (señal)
        threshold = np.max(fft_magnitude) * 0.1
        signal_indices = fft_magnitude > threshold
        
        signal_power = np.sum(fft_magnitude[signal_indices]**2)
        noise_power = np.sum(fft_magnitude[~signal_indices]**2)
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
            return float(snr)
        
        return float('inf')
    
    def find_peaks(self, data: np.ndarray, 
                  height: Optional[float] = None,
                  distance: Optional[int] = None) -> Tuple[np.ndarray, Dict]:
        """
        Encuentra picos en la señal.
        
        Args:
            data: Datos de entrada
            height: Altura mínima de los picos
            distance: Distancia mínima entre picos
            
        Returns:
            Tupla con índices de picos y propiedades
        """
        from scipy import signal
        
        peaks, properties = signal.find_peaks(data, height=height, 
                                             distance=distance)
        
        return peaks, properties
    
    def calculate_thd(self, data: np.ndarray, num_harmonics: int = 5) -> float:
        """
        Calcula la Distorsión Armónica Total (THD).
        
        Args:
            data: Datos de entrada
            num_harmonics: Número de armónicos a considerar
            
        Returns:
            THD en porcentaje
        """
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_magnitude = np.abs(fft_vals[:n//2])
        
        # Encuentra la frecuencia fundamental
        fundamental_idx = np.argmax(fft_magnitude[1:]) + 1
        fundamental_magnitude = fft_magnitude[fundamental_idx]
        
        # Calcula la potencia de los armónicos
        harmonic_power = 0.0
        for i in range(2, num_harmonics + 1):
            harmonic_idx = fundamental_idx * i
            if harmonic_idx < len(fft_magnitude):
                harmonic_power += fft_magnitude[harmonic_idx]**2
        
        # Calcula THD
        if fundamental_magnitude > 0:
            thd = 100 * np.sqrt(harmonic_power) / fundamental_magnitude
            return float(thd)
        
        return 0.0
    
    def print_analysis(self, data: np.ndarray):
        """
        Imprime un resumen completo del análisis.
        
        Args:
            data: Datos de entrada
        """
        results = self.analyze(data)
        
        print("\n" + "="*60)
        print("ANÁLISIS DE SEÑAL")
        print("="*60)
        print(f"Valor medio (DC):          {results['mean']:.4f} V")
        print(f"Valor RMS:                 {results['rms']:.4f} V")
        print(f"Pico a pico:               {results['peak_to_peak']:.4f} V")
        print(f"Valor mínimo:              {results['min']:.4f} V")
        print(f"Valor máximo:              {results['max']:.4f} V")
        print(f"Desviación estándar:       {results['std']:.4f} V")
        print(f"Varianza:                  {results['variance']:.4f} V²")
        print(f"Frecuencia fundamental:    {results['frequency']:.2f} Hz")
        print(f"Período:                   {results['period']*1000:.2f} ms")
        print(f"Ciclo de trabajo:          {results['duty_cycle']:.2f} %")
        print(f"Tiempo de subida:          {results['rise_time']*1000:.2f} ms")
        print(f"Tiempo de bajada:          {results['fall_time']*1000:.2f} ms")
        print(f"SNR:                       {results['snr']:.2f} dB")
        print("="*60 + "\n")
