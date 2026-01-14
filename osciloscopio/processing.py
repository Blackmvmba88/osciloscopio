"""
Módulo de procesamiento de señales: filtros configurables y decodificación.
"""

import numpy as np
from scipy import signal
from enum import Enum
from typing import Optional, Dict, Any


class FilterType(Enum):
    """Tipos de filtros disponibles."""
    LOWPASS = "lowpass"
    HIGHPASS = "highpass"
    BANDPASS = "bandpass"
    BANDSTOP = "bandstop"
    MOVING_AVERAGE = "moving_average"
    MEDIAN = "median"


class SignalProcessor:
    """Procesador de señales con filtros configurables."""
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa el procesador de señales.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        self.filter_config: Dict[str, Any] = {}
    
    def apply_filter(self, data: np.ndarray, filter_type: FilterType,
                    **kwargs) -> np.ndarray:
        """
        Aplica un filtro a los datos.
        
        Args:
            data: Datos a filtrar
            filter_type: Tipo de filtro a aplicar
            **kwargs: Parámetros específicos del filtro
            
        Returns:
            Datos filtrados
        """
        if filter_type == FilterType.LOWPASS:
            return self._lowpass_filter(data, **kwargs)
        elif filter_type == FilterType.HIGHPASS:
            return self._highpass_filter(data, **kwargs)
        elif filter_type == FilterType.BANDPASS:
            return self._bandpass_filter(data, **kwargs)
        elif filter_type == FilterType.BANDSTOP:
            return self._bandstop_filter(data, **kwargs)
        elif filter_type == FilterType.MOVING_AVERAGE:
            return self._moving_average_filter(data, **kwargs)
        elif filter_type == FilterType.MEDIAN:
            return self._median_filter(data, **kwargs)
        else:
            return data
    
    def _lowpass_filter(self, data: np.ndarray, cutoff: float = 50.0,
                       order: int = 4) -> np.ndarray:
        """
        Filtro paso bajo Butterworth.
        
        Args:
            data: Datos a filtrar
            cutoff: Frecuencia de corte en Hz
            order: Orden del filtro
            
        Returns:
            Datos filtrados
        """
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    
    def _highpass_filter(self, data: np.ndarray, cutoff: float = 1.0,
                        order: int = 4) -> np.ndarray:
        """
        Filtro paso alto Butterworth.
        
        Args:
            data: Datos a filtrar
            cutoff: Frecuencia de corte en Hz
            order: Orden del filtro
            
        Returns:
            Datos filtrados
        """
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = cutoff / nyquist
        b, a = signal.butter(order, normal_cutoff, btype='high', analog=False)
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    
    def _bandpass_filter(self, data: np.ndarray, lowcut: float = 5.0,
                        highcut: float = 50.0, order: int = 4) -> np.ndarray:
        """
        Filtro paso banda Butterworth.
        
        Args:
            data: Datos a filtrar
            lowcut: Frecuencia de corte inferior en Hz
            highcut: Frecuencia de corte superior en Hz
            order: Orden del filtro
            
        Returns:
            Datos filtrados
        """
        nyquist = 0.5 * self.sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(order, [low, high], btype='band', analog=False)
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    
    def _bandstop_filter(self, data: np.ndarray, lowcut: float = 45.0,
                        highcut: float = 55.0, order: int = 4) -> np.ndarray:
        """
        Filtro rechaza banda (notch) Butterworth.
        
        Args:
            data: Datos a filtrar
            lowcut: Frecuencia de corte inferior en Hz
            highcut: Frecuencia de corte superior en Hz
            order: Orden del filtro
            
        Returns:
            Datos filtrados
        """
        nyquist = 0.5 * self.sample_rate
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = signal.butter(order, [low, high], btype='bandstop', analog=False)
        filtered_data = signal.filtfilt(b, a, data)
        return filtered_data
    
    def _moving_average_filter(self, data: np.ndarray, 
                               window_size: int = 5) -> np.ndarray:
        """
        Filtro de media móvil.
        
        Args:
            data: Datos a filtrar
            window_size: Tamaño de la ventana
            
        Returns:
            Datos filtrados
        """
        window = np.ones(window_size) / window_size
        filtered_data = np.convolve(data, window, mode='same')
        return filtered_data
    
    def _median_filter(self, data: np.ndarray, 
                      kernel_size: int = 5) -> np.ndarray:
        """
        Filtro de mediana.
        
        Args:
            data: Datos a filtrar
            kernel_size: Tamaño del kernel
            
        Returns:
            Datos filtrados
        """
        filtered_data = signal.medfilt(data, kernel_size=kernel_size)
        return filtered_data
    
    def remove_dc_offset(self, data: np.ndarray) -> np.ndarray:
        """
        Elimina el componente DC de la señal.
        
        Args:
            data: Datos de entrada
            
        Returns:
            Datos sin componente DC
        """
        return data - np.mean(data)
    
    def normalize(self, data: np.ndarray, 
                 target_range: tuple = (-1.0, 1.0)) -> np.ndarray:
        """
        Normaliza la señal a un rango específico.
        
        Args:
            data: Datos de entrada
            target_range: Rango objetivo (min, max)
            
        Returns:
            Datos normalizados
        """
        data_min = np.min(data)
        data_max = np.max(data)
        
        if data_max - data_min == 0:
            return np.zeros_like(data)
        
        normalized = (data - data_min) / (data_max - data_min)
        target_min, target_max = target_range
        scaled = normalized * (target_max - target_min) + target_min
        
        return scaled
    
    def downsample(self, data: np.ndarray, factor: int) -> np.ndarray:
        """
        Reduce la frecuencia de muestreo.
        
        Args:
            data: Datos de entrada
            factor: Factor de reducción
            
        Returns:
            Datos submuestreados
        """
        return data[::factor]
    
    def detect_edges(self, data: np.ndarray, 
                    threshold: Optional[float] = None) -> tuple:
        """
        Detecta flancos ascendentes y descendentes.
        
        Args:
            data: Datos de entrada
            threshold: Umbral de detección (None = auto)
            
        Returns:
            Tupla con índices de flancos (ascendentes, descendentes)
        """
        if threshold is None:
            threshold = (np.max(data) + np.min(data)) / 2
        
        # Convierte a valores binarios
        binary = data > threshold
        
        # Detecta cambios
        diff = np.diff(binary.astype(int))
        
        rising_edges = np.where(diff > 0)[0]
        falling_edges = np.where(diff < 0)[0]
        
        return rising_edges, falling_edges
    
    def decode_pwm(self, data: np.ndarray, 
                   threshold: Optional[float] = None) -> Dict[str, float]:
        """
        Decodifica señales PWM.
        
        Args:
            data: Datos de entrada
            threshold: Umbral de detección
            
        Returns:
            Diccionario con información de la señal PWM
        """
        rising, falling = self.detect_edges(data, threshold)
        
        if len(rising) == 0 or len(falling) == 0:
            return {'duty_cycle': 0.0, 'frequency': 0.0, 'period': 0.0}
        
        # Calcula ciclos de trabajo
        duty_cycles = []
        for i in range(min(len(rising), len(falling))):
            if i < len(falling) and rising[i] < falling[i]:
                on_time = falling[i] - rising[i]
                if i + 1 < len(rising):
                    period = rising[i + 1] - rising[i]
                    if period > 0:
                        duty_cycles.append(on_time / period)
        
        avg_duty_cycle = np.mean(duty_cycles) if duty_cycles else 0.0
        
        # Calcula frecuencia
        if len(rising) > 1:
            periods = np.diff(rising)
            avg_period_samples = np.mean(periods)
            avg_period_seconds = avg_period_samples / self.sample_rate
            frequency = 1.0 / avg_period_seconds if avg_period_seconds > 0 else 0.0
        else:
            frequency = 0.0
            avg_period_seconds = 0.0
        
        return {
            'duty_cycle': avg_duty_cycle * 100,  # en porcentaje
            'frequency': frequency,
            'period': avg_period_seconds
        }
