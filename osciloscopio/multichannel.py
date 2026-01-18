"""
Módulo de soporte multi-canal para captura y análisis simultáneo de múltiples señales.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class CouplingMode(Enum):
    """Modos de acoplamiento del canal."""
    DC = "dc"
    AC = "ac"
    GND = "gnd"


@dataclass
class ChannelConfig:
    """Configuración de un canal individual."""
    enabled: bool = True
    coupling: CouplingMode = CouplingMode.DC
    vertical_scale: float = 1.0  # Voltios por división
    vertical_offset: float = 0.0  # Offset en voltios
    probe_attenuation: float = 1.0  # Factor de atenuación de la sonda
    bandwidth_limit: Optional[float] = None  # Límite de ancho de banda en Hz
    label: str = ""
    color: str = "blue"


class MultiChannelManager:
    """Gestor de múltiples canales de captura."""
    
    def __init__(self, num_channels: int = 4, sample_rate: float = 1000.0):
        """
        Inicializa el gestor de canales.
        
        Args:
            num_channels: Número de canales disponibles
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.num_channels = num_channels
        self.sample_rate = sample_rate
        
        # Configuración de cada canal
        self.channels: Dict[int, ChannelConfig] = {}
        for i in range(num_channels):
            self.channels[i] = ChannelConfig(
                label=f"CH{i+1}",
                color=self._get_default_color(i)
            )
        
        # Buffer de datos por canal
        self.channel_data: Dict[int, Optional[np.ndarray]] = {i: None for i in range(num_channels)}
        
        # Metadata
        self.time_base: float = 1.0  # segundos por división
        self.horizontal_offset: float = 0.0  # offset temporal en segundos
    
    def _get_default_color(self, channel: int) -> str:
        """Obtiene el color por defecto para un canal."""
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
                  "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
        return colors[channel % len(colors)]
    
    def configure_channel(self, channel: int, **kwargs):
        """
        Configura un canal específico.
        
        Args:
            channel: Número de canal (0-based)
            **kwargs: Parámetros de configuración (ver ChannelConfig)
        """
        if channel not in self.channels:
            raise ValueError(f"Canal {channel} no existe. Canales disponibles: 0-{self.num_channels-1}")
        
        for key, value in kwargs.items():
            if hasattr(self.channels[channel], key):
                if key == 'coupling' and isinstance(value, str):
                    value = CouplingMode(value)
                setattr(self.channels[channel], key, value)
    
    def enable_channel(self, channel: int, enabled: bool = True):
        """Habilita o deshabilita un canal."""
        if channel in self.channels:
            self.channels[channel].enabled = enabled
    
    def set_channel_data(self, channel: int, data: np.ndarray):
        """
        Establece los datos de un canal.
        
        Args:
            channel: Número de canal
            data: Datos del canal
        """
        if channel not in self.channels:
            raise ValueError(f"Canal {channel} no existe")
        
        # Aplicar configuración del canal
        processed_data = self._apply_channel_config(data, channel)
        self.channel_data[channel] = processed_data
    
    def _apply_channel_config(self, data: np.ndarray, channel: int) -> np.ndarray:
        """
        Aplica la configuración del canal a los datos.
        
        Args:
            data: Datos crudos
            channel: Número de canal
            
        Returns:
            Datos procesados según configuración
        """
        config = self.channels[channel]
        processed = data.copy()
        
        # Aplicar atenuación de sonda
        processed = processed * config.probe_attenuation
        
        # Aplicar escala vertical
        processed = processed * config.vertical_scale
        
        # Aplicar offset vertical
        processed = processed + config.vertical_offset
        
        # Aplicar acoplamiento
        if config.coupling == CouplingMode.AC:
            # Eliminar componente DC
            processed = processed - np.mean(processed)
        elif config.coupling == CouplingMode.GND:
            # Conectar a tierra
            processed = np.zeros_like(processed)
        
        return processed
    
    def get_channel_data(self, channel: int) -> Optional[np.ndarray]:
        """Obtiene los datos de un canal."""
        return self.channel_data.get(channel)
    
    def get_enabled_channels(self) -> List[int]:
        """Obtiene la lista de canales habilitados."""
        return [ch for ch, config in self.channels.items() if config.enabled]
    
    def get_all_data(self, only_enabled: bool = True) -> Dict[int, np.ndarray]:
        """
        Obtiene los datos de todos los canales.
        
        Args:
            only_enabled: Si True, solo retorna canales habilitados
            
        Returns:
            Diccionario con datos por canal
        """
        if only_enabled:
            channels = self.get_enabled_channels()
        else:
            channels = list(self.channels.keys())
        
        return {ch: self.channel_data[ch] for ch in channels if self.channel_data[ch] is not None}
    
    def clear_channel(self, channel: int):
        """Limpia los datos de un canal."""
        if channel in self.channel_data:
            self.channel_data[channel] = None
    
    def clear_all(self):
        """Limpia los datos de todos los canales."""
        for channel in self.channel_data:
            self.channel_data[channel] = None
    
    def cross_channel_analysis(self, channel_a: int, channel_b: int) -> Dict[str, Any]:
        """
        Realiza análisis cruzado entre dos canales.
        
        Args:
            channel_a: Primer canal
            channel_b: Segundo canal
            
        Returns:
            Diccionario con métricas de análisis cruzado
        """
        data_a = self.get_channel_data(channel_a)
        data_b = self.get_channel_data(channel_b)
        
        if data_a is None or data_b is None:
            return {}
        
        # Asegurar que tienen la misma longitud
        min_len = min(len(data_a), len(data_b))
        data_a = data_a[:min_len]
        data_b = data_b[:min_len]
        
        # Correlación cruzada
        correlation = np.correlate(data_a, data_b, mode='valid')[0] / min_len
        
        # Diferencia de fase (estimación simple)
        fft_a = np.fft.fft(data_a)
        fft_b = np.fft.fft(data_b)
        
        # Obtener fase del componente fundamental
        idx = np.argmax(np.abs(fft_a[1:len(fft_a)//2])) + 1
        phase_a = np.angle(fft_a[idx])
        phase_b = np.angle(fft_b[idx])
        phase_diff = np.degrees(phase_b - phase_a)
        
        # Normalizar a [-180, 180]
        while phase_diff > 180:
            phase_diff -= 360
        while phase_diff < -180:
            phase_diff += 360
        
        # Delay entre canales (en muestras)
        cross_corr = np.correlate(data_a, data_b, mode='full')
        delay_samples = len(data_a) - 1 - np.argmax(cross_corr)
        delay_time = delay_samples / self.sample_rate
        
        return {
            'correlation': float(correlation),
            'phase_difference_deg': float(phase_diff),
            'delay_samples': int(delay_samples),
            'delay_time_s': float(delay_time),
            'rms_ratio': float(np.sqrt(np.mean(data_b**2)) / np.sqrt(np.mean(data_a**2))),
        }
    
    def get_channel_info(self, channel: int) -> Dict[str, Any]:
        """
        Obtiene información de un canal.
        
        Args:
            channel: Número de canal
            
        Returns:
            Diccionario con información del canal
        """
        if channel not in self.channels:
            return {}
        
        config = self.channels[channel]
        data = self.channel_data.get(channel)
        
        info = {
            'channel': channel,
            'label': config.label,
            'enabled': config.enabled,
            'coupling': config.coupling.value,
            'vertical_scale': config.vertical_scale,
            'vertical_offset': config.vertical_offset,
            'probe_attenuation': config.probe_attenuation,
            'bandwidth_limit': config.bandwidth_limit,
            'color': config.color,
            'has_data': data is not None,
        }
        
        if data is not None:
            info['samples'] = len(data)
            info['min'] = float(np.min(data))
            info['max'] = float(np.max(data))
            info['mean'] = float(np.mean(data))
        
        return info
    
    def get_all_channels_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de todos los canales."""
        return [self.get_channel_info(ch) for ch in range(self.num_channels)]
    
    def math_operation(self, operation: str, channel_a: int, channel_b: int, 
                       result_channel: Optional[int] = None) -> np.ndarray:
        """
        Realiza operaciones matemáticas entre canales.
        
        Args:
            operation: Operación a realizar ('add', 'subtract', 'multiply', 'divide')
            channel_a: Primer canal
            channel_b: Segundo canal
            result_channel: Canal donde guardar el resultado (opcional)
            
        Returns:
            Resultado de la operación
        """
        data_a = self.get_channel_data(channel_a)
        data_b = self.get_channel_data(channel_b)
        
        if data_a is None or data_b is None:
            raise ValueError("Ambos canales deben tener datos")
        
        # Asegurar misma longitud
        min_len = min(len(data_a), len(data_b))
        data_a = data_a[:min_len]
        data_b = data_b[:min_len]
        
        # Realizar operación
        if operation == 'add':
            result = data_a + data_b
        elif operation == 'subtract':
            result = data_a - data_b
        elif operation == 'multiply':
            result = data_a * data_b
        elif operation == 'divide':
            # Evitar división por cero
            result = np.divide(data_a, data_b, where=data_b!=0, out=np.zeros_like(data_a))
        else:
            raise ValueError(f"Operación no soportada: {operation}")
        
        # Guardar en canal resultado si se especifica
        if result_channel is not None:
            self.set_channel_data(result_channel, result)
        
        return result
    
    def configure_timebase(self, time_per_div: float, offset: float = 0.0):
        """
        Configura la base de tiempo.
        
        Args:
            time_per_div: Tiempo por división en segundos
            offset: Offset temporal en segundos
        """
        self.time_base = time_per_div
        self.horizontal_offset = offset
    
    def get_time_array(self, num_samples: int) -> np.ndarray:
        """
        Genera un array de tiempo basado en la configuración actual.
        
        Args:
            num_samples: Número de muestras
            
        Returns:
            Array de tiempo en segundos
        """
        time = np.arange(num_samples) / self.sample_rate
        return time + self.horizontal_offset
