"""
Osciloscopio Digital - Sistema de captura y análisis de señales
"""

__version__ = "0.2.0"

from .acquisition import SignalSource, HardwareSource, SimulatedSource
from .processing import SignalProcessor, FilterType
from .visualization import SignalVisualizer
from .analyzer import SignalAnalyzer
from .oscilloscope import DigitalOscilloscope
from .trigger import TriggerSystem, TriggerType, TriggerMode, TriggerConfig
from .multichannel import MultiChannelManager, ChannelConfig, CouplingMode
from .protocols import (
    ProtocolDecoder, UARTDecoder, I2CDecoder, SPIDecoder, CANDecoder,
    UARTFrame, I2CTransaction, SPITransaction, UARTParity, I2COperation
)
from .advanced_analysis import (
    DigitalPersistence, AdvancedSpectralAnalysis, CalibrationSystem
)

__all__ = [
    'SignalSource',
    'HardwareSource',
    'SimulatedSource',
    'SignalProcessor',
    'FilterType',
    'SignalVisualizer',
    'SignalAnalyzer',
    'DigitalOscilloscope',
    'TriggerSystem',
    'TriggerType',
    'TriggerMode',
    'TriggerConfig',
    'MultiChannelManager',
    'ChannelConfig',
    'CouplingMode',
    'ProtocolDecoder',
    'UARTDecoder',
    'I2CDecoder',
    'SPIDecoder',
    'CANDecoder',
    'UARTFrame',
    'I2CTransaction',
    'SPITransaction',
    'UARTParity',
    'I2COperation',
    'DigitalPersistence',
    'AdvancedSpectralAnalysis',
    'CalibrationSystem',
]
