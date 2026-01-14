"""
Módulo de visualización interactiva de señales.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from typing import Optional, List, Tuple
import matplotlib.animation as animation


class SignalVisualizer:
    """Visualizador interactivo de señales."""
    
    def __init__(self, sample_rate: float = 1000.0):
        """
        Inicializa el visualizador.
        
        Args:
            sample_rate: Frecuencia de muestreo en Hz
        """
        self.sample_rate = sample_rate
        self.fig: Optional[Figure] = None
        self.axes: List = []
        
    def plot_signal(self, data: np.ndarray, title: str = "Señal",
                   xlabel: str = "Tiempo (s)", ylabel: str = "Amplitud (V)",
                   show_grid: bool = True, save_path: Optional[str] = None):
        """
        Visualiza una señal en el dominio del tiempo.
        
        Args:
            data: Datos a visualizar
            title: Título del gráfico
            xlabel: Etiqueta del eje X
            ylabel: Etiqueta del eje Y
            show_grid: Si mostrar la rejilla
            save_path: Ruta para guardar la figura (None = no guardar)
        """
        t = np.arange(len(data)) / self.sample_rate
        
        plt.figure(figsize=(12, 6))
        plt.plot(t, data, linewidth=1.5, color='#2E86AB')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        
        if show_grid:
            plt.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico guardado en: {save_path}")
        
        plt.show()
    
    def plot_multiple_signals(self, signals: List[np.ndarray], 
                             labels: List[str],
                             title: str = "Comparación de Señales",
                             save_path: Optional[str] = None):
        """
        Visualiza múltiples señales en el mismo gráfico.
        
        Args:
            signals: Lista de señales
            labels: Lista de etiquetas
            title: Título del gráfico
            save_path: Ruta para guardar la figura
        """
        plt.figure(figsize=(12, 6))
        
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
        
        for i, (signal_data, label) in enumerate(zip(signals, labels)):
            t = np.arange(len(signal_data)) / self.sample_rate
            color = colors[i % len(colors)]
            plt.plot(t, signal_data, label=label, linewidth=1.5, 
                    color=color, alpha=0.8)
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel("Tiempo (s)", fontsize=12)
        plt.ylabel("Amplitud (V)", fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico guardado en: {save_path}")
        
        plt.show()
    
    def plot_fft(self, data: np.ndarray, title: str = "Espectro de Frecuencia",
                max_freq: Optional[float] = None,
                save_path: Optional[str] = None):
        """
        Visualiza el espectro de frecuencia de una señal.
        
        Args:
            data: Datos de entrada
            title: Título del gráfico
            max_freq: Frecuencia máxima a mostrar
            save_path: Ruta para guardar la figura
        """
        # Calcula FFT
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(n, 1/self.sample_rate)
        
        # Solo frecuencias positivas
        positive_freq_idx = fft_freq >= 0
        fft_freq = fft_freq[positive_freq_idx]
        fft_magnitude = np.abs(fft_vals[positive_freq_idx])
        
        # Limita el rango de frecuencias si se especifica
        if max_freq:
            freq_mask = fft_freq <= max_freq
            fft_freq = fft_freq[freq_mask]
            fft_magnitude = fft_magnitude[freq_mask]
        
        plt.figure(figsize=(12, 6))
        plt.plot(fft_freq, fft_magnitude, linewidth=1.5, color='#A23B72')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel("Frecuencia (Hz)", fontsize=12)
        plt.ylabel("Magnitud", fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico guardado en: {save_path}")
        
        plt.show()
    
    def plot_spectrogram(self, data: np.ndarray, 
                        title: str = "Espectrograma",
                        nperseg: int = 256,
                        save_path: Optional[str] = None):
        """
        Visualiza el espectrograma de una señal.
        
        Args:
            data: Datos de entrada
            title: Título del gráfico
            nperseg: Longitud de cada segmento
            save_path: Ruta para guardar la figura
        """
        plt.figure(figsize=(12, 6))
        
        from scipy import signal as scipy_signal
        f, t, Sxx = scipy_signal.spectrogram(data, self.sample_rate, 
                                            nperseg=nperseg)
        
        plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), 
                      shading='gouraud', cmap='viridis')
        plt.colorbar(label='Potencia (dB)')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel("Tiempo (s)", fontsize=12)
        plt.ylabel("Frecuencia (Hz)", fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico guardado en: {save_path}")
        
        plt.show()
    
    def plot_xy(self, x_data: np.ndarray, y_data: np.ndarray,
               title: str = "Modo XY", xlabel: str = "Canal X",
               ylabel: str = "Canal Y", save_path: Optional[str] = None):
        """
        Visualiza dos señales en modo XY (figuras de Lissajous).
        
        Args:
            x_data: Datos del canal X
            y_data: Datos del canal Y
            title: Título del gráfico
            xlabel: Etiqueta del eje X
            ylabel: Etiqueta del eje Y
            save_path: Ruta para guardar la figura
        """
        plt.figure(figsize=(8, 8))
        plt.plot(x_data, y_data, linewidth=1.5, color='#F18F01', alpha=0.7)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.axis('equal')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Gráfico guardado en: {save_path}")
        
        plt.show()
    
    def create_dashboard(self, data: np.ndarray, filtered_data: np.ndarray,
                        title: str = "Dashboard de Análisis",
                        save_path: Optional[str] = None):
        """
        Crea un dashboard completo con múltiples visualizaciones.
        
        Args:
            data: Señal original
            filtered_data: Señal filtrada
            title: Título del dashboard
            save_path: Ruta para guardar la figura
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        t = np.arange(len(data)) / self.sample_rate
        
        # Gráfico 1: Señal original
        axes[0, 0].plot(t, data, linewidth=1, color='#2E86AB', alpha=0.7)
        axes[0, 0].set_title("Señal Original", fontweight='bold')
        axes[0, 0].set_xlabel("Tiempo (s)")
        axes[0, 0].set_ylabel("Amplitud (V)")
        axes[0, 0].grid(True, alpha=0.3, linestyle='--')
        
        # Gráfico 2: Señal filtrada
        axes[0, 1].plot(t, filtered_data, linewidth=1, color='#A23B72')
        axes[0, 1].set_title("Señal Filtrada", fontweight='bold')
        axes[0, 1].set_xlabel("Tiempo (s)")
        axes[0, 1].set_ylabel("Amplitud (V)")
        axes[0, 1].grid(True, alpha=0.3, linestyle='--')
        
        # Gráfico 3: FFT de señal original
        n = len(data)
        fft_vals = np.fft.fft(data)
        fft_freq = np.fft.fftfreq(n, 1/self.sample_rate)
        positive_idx = fft_freq >= 0
        axes[1, 0].plot(fft_freq[positive_idx], 
                       np.abs(fft_vals[positive_idx]),
                       linewidth=1, color='#F18F01')
        axes[1, 0].set_title("Espectro de Frecuencia", fontweight='bold')
        axes[1, 0].set_xlabel("Frecuencia (Hz)")
        axes[1, 0].set_ylabel("Magnitud")
        axes[1, 0].grid(True, alpha=0.3, linestyle='--')
        
        # Gráfico 4: Histograma
        axes[1, 1].hist(data, bins=50, color='#6A994E', alpha=0.7, 
                       edgecolor='black')
        axes[1, 1].set_title("Distribución de Amplitudes", fontweight='bold')
        axes[1, 1].set_xlabel("Amplitud (V)")
        axes[1, 1].set_ylabel("Frecuencia")
        axes[1, 1].grid(True, alpha=0.3, linestyle='--', axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Dashboard guardado en: {save_path}")
        
        plt.show()
