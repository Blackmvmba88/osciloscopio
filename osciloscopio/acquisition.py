"""
Módulo de adquisición de señales desde hardware externo o fuentes simuladas.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import serial
import time


class SignalSource(ABC):
    """Clase base abstracta para fuentes de señales."""
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa la fuente de señales.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        self._is_running = False
    
    @abstractmethod
    def read_samples(self, num_samples: int) -> np.ndarray:
        """
        Lee un número específico de muestras.
        
        Args:
            num_samples: Número de muestras a leer
            
        Returns:
            Array de numpy con las muestras
        """
        pass
    
    @abstractmethod
    def start(self):
        """Inicia la captura de señales."""
        pass
    
    @abstractmethod
    def stop(self):
        """Detiene la captura de señales."""
        pass
    
    def is_running(self) -> bool:
        """Retorna True si la fuente está capturando señales."""
        return self._is_running


class HardwareSource(SignalSource):
    """Fuente de señales desde hardware externo (puerto serial)."""
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200, 
                 sample_rate: float = 1000.0, voltage_range: Tuple[float, float] = (-5.0, 5.0)):
        """
        Inicializa la fuente de hardware.
        
        Args:
            port: Puerto serial para comunicación
            baudrate: Velocidad de comunicación
            sample_rate: Frecuencia de muestreo en Hz
            voltage_range: Rango de voltaje (min, max)
        """
        super().__init__(sample_rate)
        self.port = port
        self.baudrate = baudrate
        self.voltage_range = voltage_range
        self.serial_connection: Optional[serial.Serial] = None
    
    def start(self):
        """Inicia la conexión con el hardware."""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0
            )
            self._is_running = True
            print(f"Conectado a {self.port} a {self.baudrate} baudios")
        except serial.SerialException as e:
            print(f"Error al conectar con hardware: {e}")
            print("Modo simulación activado")
            self._is_running = False
    
    def stop(self):
        """Detiene la conexión con el hardware."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self._is_running = False
    
    def read_samples(self, num_samples: int) -> np.ndarray:
        """
        Lee muestras desde el hardware.
        
        Args:
            num_samples: Número de muestras a leer
            
        Returns:
            Array con las muestras leídas
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            # Si no hay conexión, retorna señal simulada
            print("Hardware no disponible, usando señal simulada")
            return self._simulate_samples(num_samples)
        
        samples = []
        try:
            for _ in range(num_samples):
                # Lee datos del puerto serial
                data = self.serial_connection.readline().decode('utf-8').strip()
                if data:
                    try:
                        value = float(data)
                        samples.append(value)
                    except ValueError:
                        samples.append(0.0)
                else:
                    samples.append(0.0)
        except Exception as e:
            print(f"Error leyendo datos: {e}")
            return self._simulate_samples(num_samples)
        
        return np.array(samples)
    
    def _simulate_samples(self, num_samples: int) -> np.ndarray:
        """Genera muestras simuladas si el hardware no está disponible."""
        t = np.linspace(0, num_samples / self.sample_rate, num_samples)
        signal = 2.5 * np.sin(2 * np.pi * 10 * t) + 0.5 * np.random.randn(num_samples)
        return signal


class SimulatedSource(SignalSource):
    """Fuente de señales simuladas para prototipado y pruebas."""
    
    def __init__(self, sample_rate: float = 1000.0, signal_type: str = 'sine',
                 frequency: float = 10.0, amplitude: float = 2.5, 
                 noise_level: float = 0.1):
        """
        Inicializa la fuente simulada.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
            signal_type: Tipo de señal ('sine', 'square', 'triangle', 'sawtooth', 'mixed')
            frequency: Frecuencia de la señal en Hz
            amplitude: Amplitud de la señal
            noise_level: Nivel de ruido (desviación estándar)
        """
        super().__init__(sample_rate)
        self.signal_type = signal_type
        self.frequency = frequency
        self.amplitude = amplitude
        self.noise_level = noise_level
        self._time_offset = 0.0
    
    def start(self):
        """Inicia la generación de señales simuladas."""
        self._is_running = True
        self._time_offset = 0.0
        print(f"Generador de señales iniciado: {self.signal_type} a {self.frequency} Hz")
    
    def stop(self):
        """Detiene la generación de señales."""
        self._is_running = False
    
    def read_samples(self, num_samples: int) -> np.ndarray:
        """
        Genera muestras simuladas.
        
        Args:
            num_samples: Número de muestras a generar
            
        Returns:
            Array con las muestras generadas
        """
        t = np.linspace(self._time_offset, 
                       self._time_offset + num_samples / self.sample_rate,
                       num_samples)
        
        # Genera la señal base según el tipo
        if self.signal_type == 'sine':
            signal = self.amplitude * np.sin(2 * np.pi * self.frequency * t)
        elif self.signal_type == 'square':
            signal = self.amplitude * np.sign(np.sin(2 * np.pi * self.frequency * t))
        elif self.signal_type == 'triangle':
            signal = self.amplitude * 2 * np.abs(2 * (t * self.frequency - np.floor(t * self.frequency + 0.5))) - self.amplitude
        elif self.signal_type == 'sawtooth':
            signal = self.amplitude * 2 * (t * self.frequency - np.floor(t * self.frequency + 0.5))
        elif self.signal_type == 'mixed':
            # Señal compleja con múltiples componentes
            signal = (self.amplitude * np.sin(2 * np.pi * self.frequency * t) +
                     0.5 * self.amplitude * np.sin(2 * np.pi * 3 * self.frequency * t) +
                     0.25 * self.amplitude * np.sin(2 * np.pi * 5 * self.frequency * t))
        else:
            signal = np.zeros(num_samples)
        
        # Añade ruido
        if self.noise_level > 0:
            noise = self.noise_level * np.random.randn(num_samples)
            signal = signal + noise
        
        self._time_offset += num_samples / self.sample_rate
        
        return signal
    
    def set_parameters(self, frequency: Optional[float] = None,
                      amplitude: Optional[float] = None,
                      noise_level: Optional[float] = None):
        """
        Actualiza los parámetros de la señal.
        
        Args:
            frequency: Nueva frecuencia
            amplitude: Nueva amplitud
            noise_level: Nuevo nivel de ruido
        """
        if frequency is not None:
            self.frequency = frequency
        if amplitude is not None:
            self.amplitude = amplitude
        if noise_level is not None:
            self.noise_level = noise_level
