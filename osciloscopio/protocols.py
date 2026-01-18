"""
Módulo de decodificadores de protocolos digitales.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class UARTParity(Enum):
    """Tipos de paridad UART."""
    NONE = "none"
    EVEN = "even"
    ODD = "odd"


class I2COperation(Enum):
    """Tipos de operación I2C."""
    START = "start"
    STOP = "stop"
    READ = "read"
    WRITE = "write"
    ACK = "ack"
    NACK = "nack"


@dataclass
class UARTFrame:
    """Frame UART decodificado."""
    start_idx: int
    data: int
    parity_ok: bool
    stop_ok: bool
    error: Optional[str] = None


@dataclass
class I2CTransaction:
    """Transacción I2C decodificada."""
    operation: I2COperation
    address: Optional[int] = None
    data: Optional[int] = None
    ack: Optional[bool] = None
    start_idx: Optional[int] = None


@dataclass
class SPITransaction:
    """Transacción SPI decodificada."""
    mosi_data: int
    miso_data: int
    start_idx: int
    bits: int = 8


class UARTDecoder:
    """Decodificador de protocolo UART."""
    
    def __init__(self, baud_rate: int = 9600, data_bits: int = 8,
                 parity: UARTParity = UARTParity.NONE, stop_bits: float = 1.0,
                 sample_rate: float = 1000000.0):
        """
        Inicializa el decodificador UART.
        
        Args:
            baud_rate: Velocidad en baudios
            data_bits: Número de bits de datos (5-9)
            parity: Tipo de paridad
            stop_bits: Número de bits de stop (1, 1.5, 2)
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.sample_rate = sample_rate
        
        # Calcular muestras por bit
        self.samples_per_bit = int(sample_rate / baud_rate)
    
    def decode(self, signal: np.ndarray, threshold: float = 0.5) -> List[UARTFrame]:
        """
        Decodifica una señal UART.
        
        Args:
            signal: Señal digital (0s y 1s o analógica)
            threshold: Umbral para conversión analógica a digital
            
        Returns:
            Lista de frames decodificados
        """
        # Convertir a digital si es necesario
        digital = (signal > threshold).astype(int)
        
        frames = []
        i = 0
        
        while i < len(digital) - self.samples_per_bit * (1 + self.data_bits + 1):
            # Buscar bit de start (transición de 1 a 0)
            if i > 0 and digital[i-1] == 1 and digital[i] == 0:
                frame = self._decode_frame(digital, i)
                if frame is not None:
                    frames.append(frame)
                    # Avanzar al siguiente frame
                    total_bits = 1 + self.data_bits + (1 if self.parity != UARTParity.NONE else 0) + int(self.stop_bits)
                    i += total_bits * self.samples_per_bit
                else:
                    i += 1
            else:
                i += 1
        
        return frames
    
    def _decode_frame(self, digital: np.ndarray, start_idx: int) -> Optional[UARTFrame]:
        """
        Decodifica un frame UART individual.
        
        Args:
            digital: Señal digital
            start_idx: Índice del bit de start
            
        Returns:
            Frame decodificado o None si hay error
        """
        idx = start_idx
        
        # Verificar bit de start
        start_sample = idx + self.samples_per_bit // 2
        if start_sample >= len(digital) or digital[start_sample] != 0:
            return UARTFrame(start_idx, 0, False, False, "Invalid start bit")
        
        idx += self.samples_per_bit
        
        # Leer bits de datos (LSB primero)
        data = 0
        for bit_pos in range(self.data_bits):
            bit_sample = idx + self.samples_per_bit // 2
            if bit_sample >= len(digital):
                return UARTFrame(start_idx, 0, False, False, "Incomplete frame")
            
            bit_value = digital[bit_sample]
            data |= (bit_value << bit_pos)
            idx += self.samples_per_bit
        
        # Verificar paridad si está habilitada
        parity_ok = True
        if self.parity != UARTParity.NONE:
            parity_sample = idx + self.samples_per_bit // 2
            if parity_sample >= len(digital):
                return UARTFrame(start_idx, data, False, False, "Missing parity bit")
            
            parity_bit = digital[parity_sample]
            data_ones = bin(data).count('1')
            
            # Para EVEN parity: total de 1s (datos + parity bit) debe ser par
            # Para ODD parity: total de 1s debe ser impar
            total_ones = data_ones + parity_bit
            
            if self.parity == UARTParity.EVEN:
                parity_ok = (total_ones % 2 == 0)
            else:  # ODD
                parity_ok = (total_ones % 2 == 1)
            
            idx += self.samples_per_bit
        
        # Verificar bit(s) de stop
        stop_samples = int(self.stop_bits * self.samples_per_bit)
        stop_sample = idx + stop_samples // 2
        
        if stop_sample >= len(digital):
            return UARTFrame(start_idx, data, parity_ok, False, "Missing stop bit")
        
        stop_ok = digital[stop_sample] == 1
        
        return UARTFrame(start_idx, data, parity_ok, stop_ok)
    
    def frames_to_bytes(self, frames: List[UARTFrame]) -> bytes:
        """Convierte frames decodificados a bytes."""
        return bytes([frame.data for frame in frames if frame.parity_ok and frame.stop_ok])
    
    def frames_to_string(self, frames: List[UARTFrame], encoding: str = 'utf-8') -> str:
        """Convierte frames a string."""
        try:
            return self.frames_to_bytes(frames).decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            return ""


class I2CDecoder:
    """Decodificador de protocolo I2C."""
    
    def __init__(self, sample_rate: float = 1000000.0):
        """
        Inicializa el decodificador I2C.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
    
    def decode(self, scl: np.ndarray, sda: np.ndarray, 
               threshold: float = 0.5) -> List[I2CTransaction]:
        """
        Decodifica comunicación I2C.
        
        Args:
            scl: Señal de reloj (SCL)
            sda: Señal de datos (SDA)
            threshold: Umbral para conversión a digital
            
        Returns:
            Lista de transacciones decodificadas
        """
        # Convertir a digital
        scl_digital = (scl > threshold).astype(int)
        sda_digital = (sda > threshold).astype(int)
        
        transactions = []
        i = 1
        
        while i < len(scl_digital):
            # Detectar condición de START (SDA cae mientras SCL está alto)
            if scl_digital[i] == 1 and scl_digital[i-1] == 1:
                if sda_digital[i] == 0 and sda_digital[i-1] == 1:
                    transactions.append(I2CTransaction(I2COperation.START, start_idx=i))
                    
                    # Leer dirección y bit R/W
                    address_byte = self._read_byte(scl_digital, sda_digital, i)
                    if address_byte is not None:
                        byte_val, ack, idx = address_byte
                        address = byte_val >> 1
                        is_read = (byte_val & 0x01) == 1
                        
                        op = I2COperation.READ if is_read else I2COperation.WRITE
                        transactions.append(I2CTransaction(
                            op, address=address, ack=ack, start_idx=idx
                        ))
                        
                        i = idx
                    else:
                        i += 1
                elif sda_digital[i] == 1 and sda_digital[i-1] == 0:
                    # Condición de STOP (SDA sube mientras SCL está alto)
                    transactions.append(I2CTransaction(I2COperation.STOP, start_idx=i))
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return transactions
    
    def _read_byte(self, scl: np.ndarray, sda: np.ndarray, 
                   start_idx: int) -> Optional[Tuple[int, bool, int]]:
        """
        Lee un byte del bus I2C.
        
        Returns:
            Tupla (byte, ack, índice_final) o None
        """
        idx = start_idx
        byte_val = 0
        
        # Buscar 8 flancos de subida de SCL
        bits_read = 0
        while idx < len(scl) - 1 and bits_read < 8:
            if scl[idx] == 0 and scl[idx+1] == 1:
                # Flanco de subida de SCL, leer SDA
                bit_val = sda[idx+1]
                byte_val = (byte_val << 1) | bit_val
                bits_read += 1
            idx += 1
        
        if bits_read < 8:
            return None
        
        # Leer bit de ACK
        ack = False
        while idx < len(scl) - 1:
            if scl[idx] == 0 and scl[idx+1] == 1:
                ack = (sda[idx+1] == 0)  # ACK es 0, NACK es 1
                break
            idx += 1
        
        return (byte_val, ack, idx)


class SPIDecoder:
    """Decodificador de protocolo SPI."""
    
    def __init__(self, mode: int = 0, bit_order: str = 'msb', 
                 bits_per_word: int = 8, sample_rate: float = 1000000.0):
        """
        Inicializa el decodificador SPI.
        
        Args:
            mode: Modo SPI (0-3, define CPOL y CPHA)
            bit_order: Orden de bits ('msb' o 'lsb')
            bits_per_word: Bits por palabra
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.mode = mode
        self.bit_order = bit_order
        self.bits_per_word = bits_per_word
        self.sample_rate = sample_rate
        
        # Extraer CPOL y CPHA del modo
        self.cpol = (mode >> 1) & 1  # Clock polarity
        self.cpha = mode & 1          # Clock phase
    
    def decode(self, sclk: np.ndarray, mosi: np.ndarray, 
               miso: np.ndarray, cs: Optional[np.ndarray] = None,
               threshold: float = 0.5) -> List[SPITransaction]:
        """
        Decodifica comunicación SPI.
        
        Args:
            sclk: Señal de reloj
            mosi: Master Out Slave In
            miso: Master In Slave Out
            cs: Chip Select (opcional)
            threshold: Umbral para conversión a digital
            
        Returns:
            Lista de transacciones SPI
        """
        # Convertir a digital
        sclk_digital = (sclk > threshold).astype(int)
        mosi_digital = (mosi > threshold).astype(int)
        miso_digital = (miso > threshold).astype(int)
        
        if cs is not None:
            cs_digital = (cs > threshold).astype(int)
        else:
            cs_digital = np.zeros(len(sclk_digital), dtype=int)
        
        transactions = []
        
        # Determinar flanco de captura según CPOL y CPHA
        if self.cpha == 0:
            # Capturar en primer flanco
            capture_edge = 'rising' if self.cpol == 0 else 'falling'
        else:
            # Capturar en segundo flanco
            capture_edge = 'falling' if self.cpol == 0 else 'rising'
        
        i = 1
        while i < len(sclk_digital):
            # Verificar si CS está activo (bajo)
            if cs is not None and cs_digital[i] == 1:
                i += 1
                continue
            
            # Detectar flanco de captura
            is_capture = False
            if capture_edge == 'rising':
                is_capture = sclk_digital[i] == 1 and sclk_digital[i-1] == 0
            else:
                is_capture = sclk_digital[i] == 0 and sclk_digital[i-1] == 1
            
            if is_capture:
                # Leer palabra completa
                transaction = self._read_word(sclk_digital, mosi_digital, 
                                             miso_digital, i, capture_edge)
                if transaction is not None:
                    transactions.append(transaction)
                    i = transaction.start_idx + self.bits_per_word * 2
                else:
                    i += 1
            else:
                i += 1
        
        return transactions
    
    def _read_word(self, sclk: np.ndarray, mosi: np.ndarray, 
                   miso: np.ndarray, start_idx: int, 
                   capture_edge: str) -> Optional[SPITransaction]:
        """
        Lee una palabra SPI completa.
        
        Returns:
            Transacción SPI o None
        """
        mosi_word = 0
        miso_word = 0
        bits_read = 0
        idx = start_idx
        
        while idx < len(sclk) - 1 and bits_read < self.bits_per_word:
            # Detectar flanco de captura
            is_capture = False
            if capture_edge == 'rising':
                is_capture = sclk[idx+1] == 1 and sclk[idx] == 0
            else:
                is_capture = sclk[idx+1] == 0 and sclk[idx] == 1
            
            if is_capture:
                mosi_bit = mosi[idx+1]
                miso_bit = miso[idx+1]
                
                if self.bit_order == 'msb':
                    mosi_word = (mosi_word << 1) | mosi_bit
                    miso_word = (miso_word << 1) | miso_bit
                else:  # lsb
                    mosi_word = mosi_word | (mosi_bit << bits_read)
                    miso_word = miso_word | (miso_bit << bits_read)
                
                bits_read += 1
            
            idx += 1
        
        if bits_read < self.bits_per_word:
            return None
        
        return SPITransaction(mosi_word, miso_word, start_idx, self.bits_per_word)


class CANDecoder:
    """Decodificador de protocolo CAN (simplificado)."""
    
    def __init__(self, bit_rate: int = 500000, sample_rate: float = 10000000.0):
        """
        Inicializa el decodificador CAN.
        
        Args:
            bit_rate: Velocidad en bits por segundo
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.bit_rate = bit_rate
        self.sample_rate = sample_rate
        self.samples_per_bit = int(sample_rate / bit_rate)
    
    def decode(self, signal: np.ndarray, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Decodifica frames CAN (implementación simplificada).
        
        Args:
            signal: Señal CAN
            threshold: Umbral para conversión a digital
            
        Returns:
            Lista de frames decodificados
        """
        # Convertir a digital
        digital = (signal > threshold).astype(int)
        
        frames = []
        i = 0
        
        # Implementación simplificada: buscar SOF (Start of Frame)
        # Un frame CAN completo requiere decodificación bit stuffing, CRC, etc.
        # Esta es una versión básica para demostración
        
        while i < len(digital) - self.samples_per_bit * 20:
            # Buscar SOF (bit dominante después de idle)
            if i > 0 and digital[i-1] == 1 and digital[i] == 0:
                # Intentar leer identificador (11 bits estándar)
                identifier = 0
                idx = i + self.samples_per_bit
                
                for bit_pos in range(11):
                    if idx + self.samples_per_bit // 2 < len(digital):
                        bit_val = digital[idx + self.samples_per_bit // 2]
                        identifier = (identifier << 1) | bit_val
                        idx += self.samples_per_bit
                
                frames.append({
                    'start_idx': i,
                    'identifier': identifier,
                    'type': 'CAN',
                })
                
                i = idx
            else:
                i += 1
        
        return frames


class ProtocolDecoder:
    """Clase unificada para decodificación de múltiples protocolos."""
    
    def __init__(self, sample_rate: float = 1000000.0):
        """
        Inicializa el decodificador de protocolos.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        self.uart_decoder = None
        self.i2c_decoder = None
        self.spi_decoder = None
        self.can_decoder = None
    
    def decode_uart(self, signal: np.ndarray, **kwargs) -> List[UARTFrame]:
        """Decodifica UART."""
        if self.uart_decoder is None or kwargs:
            self.uart_decoder = UARTDecoder(sample_rate=self.sample_rate, **kwargs)
        return self.uart_decoder.decode(signal)
    
    def decode_i2c(self, scl: np.ndarray, sda: np.ndarray, **kwargs) -> List[I2CTransaction]:
        """Decodifica I2C."""
        if self.i2c_decoder is None:
            self.i2c_decoder = I2CDecoder(sample_rate=self.sample_rate)
        return self.i2c_decoder.decode(scl, sda, **kwargs)
    
    def decode_spi(self, sclk: np.ndarray, mosi: np.ndarray, 
                   miso: np.ndarray, cs: Optional[np.ndarray] = None, 
                   **kwargs) -> List[SPITransaction]:
        """Decodifica SPI."""
        if self.spi_decoder is None or kwargs:
            self.spi_decoder = SPIDecoder(sample_rate=self.sample_rate, **kwargs)
        return self.spi_decoder.decode(sclk, mosi, miso, cs)
    
    def decode_can(self, signal: np.ndarray, **kwargs) -> List[Dict[str, Any]]:
        """Decodifica CAN."""
        if self.can_decoder is None or kwargs:
            self.can_decoder = CANDecoder(sample_rate=self.sample_rate, **kwargs)
        return self.can_decoder.decode(signal)
