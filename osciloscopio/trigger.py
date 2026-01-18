"""
Módulo de triggers avanzados para captura condicional de señales.
"""

import numpy as np
from enum import Enum
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass


class TriggerType(Enum):
    """Tipos de trigger disponibles."""
    NONE = "none"
    RISING_EDGE = "rising_edge"
    FALLING_EDGE = "falling_edge"
    EITHER_EDGE = "either_edge"
    PULSE_WIDTH = "pulse_width"
    RUNT_PULSE = "runt_pulse"
    WINDOW = "window"


class TriggerMode(Enum):
    """Modos de operación del trigger."""
    AUTO = "auto"           # Trigger automático si no se encuentra condición
    NORMAL = "normal"       # Solo trigger cuando se cumple condición
    SINGLE = "single"       # Trigger único


@dataclass
class TriggerConfig:
    """Configuración del sistema de trigger."""
    trigger_type: TriggerType = TriggerType.RISING_EDGE
    mode: TriggerMode = TriggerMode.AUTO
    level: float = 0.0
    hysteresis: float = 0.1
    channel: int = 0
    
    # Para pulse width trigger
    pulse_width_min: Optional[float] = None  # en segundos
    pulse_width_max: Optional[float] = None
    
    # Para window trigger
    upper_level: Optional[float] = None
    lower_level: Optional[float] = None
    
    # Para runt pulse
    upper_threshold: Optional[float] = None
    lower_threshold: Optional[float] = None
    
    # Holdoff time (tiempo mínimo entre triggers)
    holdoff: float = 0.0  # en segundos


class TriggerSystem:
    """Sistema de triggers avanzado para captura condicional."""
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa el sistema de triggers.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        self.config = TriggerConfig()
        self._last_trigger_idx = -1
    
    def configure(self, **kwargs):
        """
        Configura el sistema de triggers.
        
        Args:
            **kwargs: Parámetros de configuración (ver TriggerConfig)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                if key == 'trigger_type' and isinstance(value, str):
                    value = TriggerType(value)
                elif key == 'mode' and isinstance(value, str):
                    value = TriggerMode(value)
                setattr(self.config, key, value)
    
    def find_trigger(self, data: np.ndarray, channel: int = 0) -> Optional[int]:
        """
        Encuentra el índice donde se cumple la condición de trigger.
        
        Args:
            data: Datos de señal
            channel: Canal a analizar (para sistemas multi-canal)
            
        Returns:
            Índice del trigger o None si no se encuentra
        """
        if self.config.trigger_type == TriggerType.NONE:
            return 0
        
        if self.config.trigger_type == TriggerType.RISING_EDGE:
            return self._find_rising_edge(data)
        elif self.config.trigger_type == TriggerType.FALLING_EDGE:
            return self._find_falling_edge(data)
        elif self.config.trigger_type == TriggerType.EITHER_EDGE:
            rising = self._find_rising_edge(data)
            falling = self._find_falling_edge(data)
            if rising is None:
                return falling
            if falling is None:
                return rising
            return min(rising, falling)
        elif self.config.trigger_type == TriggerType.PULSE_WIDTH:
            return self._find_pulse_width(data)
        elif self.config.trigger_type == TriggerType.RUNT_PULSE:
            return self._find_runt_pulse(data)
        elif self.config.trigger_type == TriggerType.WINDOW:
            return self._find_window_trigger(data)
        
        return None
    
    def _find_rising_edge(self, data: np.ndarray) -> Optional[int]:
        """
        Encuentra un flanco de subida que cruza el nivel de trigger.
        
        Args:
            data: Datos de señal
            
        Returns:
            Índice del trigger o None
        """
        level = self.config.level
        hysteresis = self.config.hysteresis
        holdoff_samples = int(self.config.holdoff * self.sample_rate)
        
        # Buscar cruce de umbral con histéresis
        below_threshold = data < (level - hysteresis)
        above_threshold = data > (level + hysteresis)
        
        # Estado inicial
        state = 'searching'
        
        for i in range(1, len(data)):
            # Aplicar holdoff
            if self._last_trigger_idx >= 0:
                if i - self._last_trigger_idx < holdoff_samples:
                    continue
            
            if state == 'searching' and below_threshold[i-1]:
                state = 'below'
            elif state == 'below' and above_threshold[i]:
                self._last_trigger_idx = i
                return i
        
        return None
    
    def _find_falling_edge(self, data: np.ndarray) -> Optional[int]:
        """
        Encuentra un flanco de bajada que cruza el nivel de trigger.
        
        Args:
            data: Datos de señal
            
        Returns:
            Índice del trigger o None
        """
        level = self.config.level
        hysteresis = self.config.hysteresis
        holdoff_samples = int(self.config.holdoff * self.sample_rate)
        
        # Buscar cruce de umbral con histéresis
        below_threshold = data < (level - hysteresis)
        above_threshold = data > (level + hysteresis)
        
        # Estado inicial
        state = 'searching'
        
        for i in range(1, len(data)):
            # Aplicar holdoff
            if self._last_trigger_idx >= 0:
                if i - self._last_trigger_idx < holdoff_samples:
                    continue
            
            if state == 'searching' and above_threshold[i-1]:
                state = 'above'
            elif state == 'above' and below_threshold[i]:
                self._last_trigger_idx = i
                return i
        
        return None
    
    def _find_pulse_width(self, data: np.ndarray) -> Optional[int]:
        """
        Encuentra un pulso con ancho específico.
        
        Args:
            data: Datos de señal
            
        Returns:
            Índice del trigger o None
        """
        if self.config.pulse_width_min is None and self.config.pulse_width_max is None:
            return None
        
        level = self.config.level
        hysteresis = self.config.hysteresis
        
        # Convertir tiempos a muestras
        width_min_samples = 0
        width_max_samples = len(data)
        
        if self.config.pulse_width_min is not None:
            width_min_samples = int(self.config.pulse_width_min * self.sample_rate)
        if self.config.pulse_width_max is not None:
            width_max_samples = int(self.config.pulse_width_max * self.sample_rate)
        
        # Detectar pulsos
        above_threshold = data > (level + hysteresis)
        
        pulse_start = None
        for i in range(len(data)):
            if above_threshold[i] and pulse_start is None:
                pulse_start = i
            elif not above_threshold[i] and pulse_start is not None:
                pulse_width = i - pulse_start
                if width_min_samples <= pulse_width <= width_max_samples:
                    return pulse_start
                pulse_start = None
        
        return None
    
    def _find_runt_pulse(self, data: np.ndarray) -> Optional[int]:
        """
        Encuentra un pulso runt (que no alcanza el nivel esperado).
        
        Args:
            data: Datos de señal
            
        Returns:
            Índice del trigger o None
        """
        if self.config.upper_threshold is None or self.config.lower_threshold is None:
            return None
        
        upper = self.config.upper_threshold
        lower = self.config.lower_threshold
        
        # Detectar cruces del umbral inferior pero no del superior
        above_lower = data > lower
        above_upper = data > upper
        
        pulse_start = None
        crossed_lower = False
        crossed_upper = False
        
        for i in range(len(data)):
            if above_lower[i] and pulse_start is None:
                pulse_start = i
                crossed_lower = True
                crossed_upper = False
            
            if pulse_start is not None and above_upper[i]:
                crossed_upper = True
            
            if pulse_start is not None and not above_lower[i]:
                # Fin del pulso
                if crossed_lower and not crossed_upper:
                    # Es un runt pulse
                    return pulse_start
                pulse_start = None
                crossed_lower = False
                crossed_upper = False
        
        return None
    
    def _find_window_trigger(self, data: np.ndarray) -> Optional[int]:
        """
        Encuentra cuando la señal sale de una ventana definida.
        
        Args:
            data: Datos de señal
            
        Returns:
            Índice del trigger o None
        """
        if self.config.upper_level is None or self.config.lower_level is None:
            return None
        
        upper = self.config.upper_level
        lower = self.config.lower_level
        
        # Detectar salida de la ventana
        in_window = (data >= lower) & (data <= upper)
        
        # Buscar primera salida de ventana
        for i in range(len(data)):
            if not in_window[i]:
                return i
        
        return None
    
    def apply_trigger(self, data: np.ndarray, pre_trigger_percent: float = 10.0) -> Tuple[np.ndarray, Optional[int]]:
        """
        Aplica el trigger a los datos y retorna una ventana centrada en el trigger.
        
        Args:
            data: Datos de señal
            pre_trigger_percent: Porcentaje de datos antes del trigger (0-100)
            
        Returns:
            Tupla (datos_triggered, índice_trigger)
        """
        trigger_idx = self.find_trigger(data)
        
        if trigger_idx is None:
            if self.config.mode == TriggerMode.AUTO:
                # Modo auto: retornar datos sin trigger
                return data, None
            else:
                # Modo normal/single: no hay datos válidos
                return np.array([]), None
        
        # Calcular ventana pre/post trigger
        pre_samples = int(len(data) * pre_trigger_percent / 100.0)
        
        start_idx = max(0, trigger_idx - pre_samples)
        end_idx = min(len(data), start_idx + len(data))
        
        # Ajustar si estamos cerca del final
        if end_idx - start_idx < len(data):
            start_idx = max(0, end_idx - len(data))
        
        triggered_data = data[start_idx:end_idx]
        relative_trigger_idx = trigger_idx - start_idx
        
        return triggered_data, relative_trigger_idx
    
    def reset(self):
        """Resetea el estado interno del trigger."""
        self._last_trigger_idx = -1
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del sistema de trigger.
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'type': self.config.trigger_type.value,
            'mode': self.config.mode.value,
            'level': self.config.level,
            'channel': self.config.channel,
            'last_trigger_index': self._last_trigger_idx,
        }
