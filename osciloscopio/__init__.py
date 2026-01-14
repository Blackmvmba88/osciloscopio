"""
Osciloscopio Digital - Sistema de captura y análisis de señales
"""

__version__ = "0.1.0"

from .acquisition import SignalSource, HardwareSource, SimulatedSource
from .processing import SignalProcessor, FilterType
from .visualization import SignalVisualizer
from .analyzer import SignalAnalyzer
from .oscilloscope import DigitalOscilloscope

__all__ = [
    'SignalSource',
    'HardwareSource',
    'SimulatedSource',
    'SignalProcessor',
    'FilterType',
    'SignalVisualizer',
    'SignalAnalyzer',
    'DigitalOscilloscope',
]
