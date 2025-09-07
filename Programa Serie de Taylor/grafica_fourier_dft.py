import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import square, sawtooth
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.colors as mcolors

class SignalGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador y Analizador de Señales - Professional Edition")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Variables para almacenar parámetros
        self.senal1_vars = self.create_signal_vars()
        self.senal2_vars = self.create_signal_vars()
        self.usar_canal2 = tk.BooleanVar(value=False)
        
        # Para la animación
        self.ani = None
        self.line1 = None
        self.line2 = None
        
        self.setup_ui()
        
    def configure_styles(self):
        # Configurar estilos modernos
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('Title.TLabel', 
                            background='#2c3e50', 
                            foreground='#ecf0f1', 
                            font=('Arial', 18, 'bold'))
        self.style.configure('TLabel', 
                            background='#34495e', 
                            foreground='#ecf0f1',
                            font=('Arial', 10))
        self.style.configure('TLabelframe', 
                            background='#34495e', 
                            foreground='#ecf0f1')
        self.style.configure('TLabelframe.Label', 
                            background='#34495e', 
                            foreground='#ecf0f1',
                            font=('Arial', 12, 'bold'))
        self.style.configure('TButton', 
                            background='#3498db', 
                            foreground='#ecf0f1',
                            font=('Arial', 10, 'bold'))
        self.style.map('TButton', 
                      background=[('active', '#2980b9')])
        self.style.configure('Primary.TButton', 
                            background='#2ecc71', 
                            foreground='#ecf0f1',
                            font=('Arial', 11, 'bold'))
        self.style.map('Primary.TButton', 
                      background=[('active', '#27ae60')])
        self.style.configure('TCombobox', 
                            fieldbackground='#ecf0f1',
                            background='#3498db',
                            foreground='#2c3e50')
        self.style.configure('TSpinbox', 
                            fieldbackground='#ecf0f1',
                            background='#3498db',
                            foreground='#2c3e50')
        self.style.configure('TCheckbutton', 
                            background='#34495e', 
                            foreground='#ecf0f1')
        
    def create_signal_vars(self):
        return {
            'tipo': tk.StringVar(value="seno"),
            'frecuencia': tk.DoubleVar(value=1.0),
            'amplitud': tk.DoubleVar(value=1.0),
            'muestras': tk.IntVar(value=100),
            'continua': tk.BooleanVar(value=True)
        }
    
    def setup_ui(self):
        # Frame principal con paned window para mejor distribución
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo para controles
        control_frame = ttk.Frame(main_paned, padding="15", style='TFrame')
        main_paned.add(control_frame, weight=1)
        
        # Panel derecho para gráficos
        graph_frame = ttk.Frame(main_paned, style='TFrame')
        main_paned.add(graph_frame, weight=3)
        
        # Título
        title_label = ttk.Label(control_frame, text="Generador de Señales", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Canal 1
        ch1_frame = ttk.LabelFrame(control_frame, text="Canal 1 (CH1)", padding="10")
        ch1_frame.pack(fill=tk.X, pady=5)
        
        self.create_signal_controls(ch1_frame, self.senal1_vars, 0)
        
        # Separador
        separator = ttk.Separator(control_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=15)
        
        # Canal 2
        ch2_check = ttk.Checkbutton(control_frame, text="Activar Canal 2", 
                                   variable=self.usar_canal2,
                                   command=self.toggle_canal2,
                                   style='TCheckbutton')
        ch2_check.pack(anchor=tk.W, pady=5)
        
        self.ch2_frame = ttk.LabelFrame(control_frame, text="Canal 2 (CH2)", padding="10")
        self.ch2_frame.pack(fill=tk.X, pady=5)
        
        self.create_signal_controls(self.ch2_frame, self.senal2_vars, 0)
        self.toggle_canal2()  # Inicializar estado
        
        # Botones
        button_frame = ttk.Frame(control_frame, style='TFrame')
        button_frame.pack(fill=tk.X, pady=20)
        
        generate_btn = ttk.Button(button_frame, text="Generar Gráficos", 
                                 command=self.generate_plots,
                                 style='Primary.TButton')
        generate_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        animate_btn = ttk.Button(button_frame, text="Iniciar Animación", 
                                command=self.start_animation,
                                style='TButton')
        animate_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        clear_btn = ttk.Button(button_frame, text="Limpiar", 
                              command=self.clear_plots,
                              style='TButton')
        clear_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Notebook para gráficos con pestañas
        self.notebook = ttk.Notebook(graph_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Espectro de Fourier
        tab1 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab1, text="Espectro de Fourier")
        
        # Pestaña 2: Fase y Señales
        tab2 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab2, text="Fase y Señales")
        
        # Pestaña 3: Osciloscopio
        tab3 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab3, text="Osciloscopio")
        
        # Configurar matplotlib con estilo oscuro
        plt.style.use('dark_background')
        
        # Inicializar figuras
        self.fig1, self.axs1 = plt.subplots(3, 1, figsize=(10, 8), facecolor='#2c3e50')
        self.fig2, self.axs2 = plt.subplots(2, 1, figsize=(10, 6), facecolor='#2c3e50')
        self.fig3, self.ax3 = plt.subplots(figsize=(10, 4), facecolor='#2c3e50')
        
        # Configurar colores de ejes y texto
        for fig in [self.fig1, self.fig2, self.fig3]:
            fig.patch.set_facecolor('#2c3e50')
        
        for ax in [*self.axs1, *self.axs2, self.ax3]:
            ax.set_facecolor('#34495e')
            ax.tick_params(colors='#ecf0f1')
            ax.xaxis.label.set_color('#ecf0f1')
            ax.yaxis.label.set_color('#ecf0f1')
            ax.title.set_color('#ecf0f1')
            ax.spines['bottom'].set_color('#7f8c8d')
            ax.spines['top'].set_color('#7f8c8d')
            ax.spines['right'].set_color('#7f8c8d')
            ax.spines['left'].set_color('#7f8c8d')
            ax.grid(True, color='#4a6572', linestyle='--', linewidth=0.5)
        
        # Canvas para gráficos
        self.canvas1 = FigureCanvasTkAgg(self.fig1, tab1)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, tab2)
        self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.canvas3 = FigureCanvasTkAgg(self.fig3, tab3)
        self.canvas3.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Toolbars
        self.toolbar1 = NavigationToolbar2Tk(self.canvas1, tab1)
        self.toolbar1.update()
        self.toolbar1.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, tab2)
        self.toolbar2.update()
        self.toolbar2.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.toolbar3 = NavigationToolbar2Tk(self.canvas3, tab3)
        self.toolbar3.update()
        self.toolbar3.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_signal_controls(self, parent, vars_dict, start_row):
        # Tipo de señal
        ttk.Label(parent, text="Tipo de señal:").grid(row=start_row, column=0, sticky=tk.W, pady=5)
        tipo_combo = ttk.Combobox(parent, textvariable=vars_dict['tipo'], 
                                 values=["seno", "cuadrada", "triangular"],
                                 state="readonly", width=18)
        tipo_combo.grid(row=start_row, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Frecuencia
        ttk.Label(parent, text="Frecuencia (Hz):").grid(row=start_row+1, column=0, sticky=tk.W, pady=5)
        freq_spin = ttk.Spinbox(parent, textvariable=vars_dict['frecuencia'], 
                               from_=0.1, to=1000, increment=0.1, width=18)
        freq_spin.grid(row=start_row+1, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Amplitud
        ttk.Label(parent, text="Amplitud:").grid(row=start_row+2, column=0, sticky=tk.W, pady=5)
        amp_spin = ttk.Spinbox(parent, textvariable=vars_dict['amplitud'], 
                              from_=0.1, to=10, increment=0.1, width=18)
        amp_spin.grid(row=start_row+2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Muestras
        ttk.Label(parent, text="Número de muestras:").grid(row=start_row+3, column=0, sticky=tk.W, pady=5)
        muestras_spin = ttk.Spinbox(parent, textvariable=vars_dict['muestras'], 
                                   from_=10, to=10000, increment=10, width=18)
        muestras_spin.grid(row=start_row+3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Continua/Discreta
        ttk.Checkbutton(parent, text="Señal continua", 
                       variable=vars_dict['continua'],
                       style='TCheckbutton').grid(row=start_row+4, column=0, 
                                                 columnspan=2, sticky=tk.W, pady=5)
        
        # Configurar peso de columnas para expansión
        parent.columnconfigure(1, weight=1)
    
    def toggle_canal2(self):
        if self.usar_canal2.get():
            for child in self.ch2_frame.winfo_children():
                child.configure(state='normal')
        else:
            for child in self.ch2_frame.winfo_children():
                child.configure(state='disabled')
    
    def generar_senal(self, tipo, frecuencia, muestras, amplitud, continua):
        if continua:
            t = np.linspace(0, 1, muestras)
            argumento = 2 * np.pi * frecuencia * t
        else:
            t = np.arange(muestras)
            argumento = 2 * np.pi * frecuencia * t / muestras  # Normalizado para discretas
            
        if tipo == "seno":
            senal = amplitud * np.sin(argumento)
        elif tipo == "cuadrada":
            senal = amplitud * square(argumento)
        elif tipo == "triangular":
            senal = amplitud * sawtooth(argumento, width=0.5)
        else:
            raise ValueError("Tipo de señal no válido")
        return t, senal
    
    def generate_plots(self):
        try:
            # Generar señal 1
            t1, senal1 = self.generar_senal(
                self.senal1_vars['tipo'].get(),
                self.senal1_vars['frecuencia'].get(),
                self.senal1_vars['muestras'].get(),
                self.senal1_vars['amplitud'].get(),
                self.senal1_vars['continua'].get()
            )
            
            # Generar señal 2 si está activado
            if self.usar_canal2.get():
                t2, senal2 = self.generar_senal(
                    self.senal2_vars['tipo'].get(),
                    self.senal2_vars['frecuencia'].get(),
                    self.senal2_vars['muestras'].get(),
                    self.senal2_vars['amplitud'].get(),
                    self.senal2_vars['continua'].get()
                )
            else:
                muestras2 = self.senal1_vars['muestras'].get()
                t2 = t1
                senal2 = np.zeros(muestras2)
            
            # Ajuste para mismo tamaño
            muestras1 = len(senal1)
            muestras2 = len(senal2)
            muestras = max(muestras1, muestras2)
            
            if len(senal1) < muestras:
                senal1 = np.pad(senal1, (0, muestras - len(senal1)))
            if len(senal2) < muestras:
                senal2 = np.pad(senal2, (0, muestras - len(senal2)))
            
            t_anim = np.arange(muestras)
            
            # Calcular FFT
            fft1 = np.fft.fft(senal1)
            fft2 = np.fft.fft(senal2)
            frecuencias = np.fft.fftfreq(muestras, d=1.0 / muestras)
            
            magnitude1 = np.abs(fft1)
            magnitude2 = np.abs(fft2)
            real1 = np.real(fft1)
            real2 = np.real(fft2)
            imag1 = np.imag(fft1)
            imag2 = np.imag(fft2)
            phase1 = np.angle(fft1)
            phase2 = np.angle(fft2)
            
            # Limpiar gráficos anteriores
            for ax in self.axs1:
                ax.clear()
            for ax in self.axs2:
                ax.clear()
            self.ax3.clear()
            
            # Configurar estilos de ejes después de limpiar
            for ax in [*self.axs1, *self.axs2, self.ax3]:
                ax.set_facecolor('#34495e')
                ax.tick_params(colors='#ecf0f1')
                ax.xaxis.label.set_color('#ecf0f1')
                ax.yaxis.label.set_color('#ecf0f1')
                ax.title.set_color('#ecf0f1')
                ax.spines['bottom'].set_color('#7f8c8d')
                ax.spines['top'].set_color('#7f8c8d')
                ax.spines['right'].set_color('#7f8c8d')
                ax.spines['left'].set_color('#7f8c8d')
                ax.grid(True, color='#4a6572', linestyle='--', linewidth=0.5)
            
            # Ventana 1: Espectro, Real, Imaginario
            self.axs1[0].plot(frecuencias[:muestras // 2], magnitude1[:muestras // 2], 'cyan', label='CH1', linewidth=2)
            if self.usar_canal2.get():
                self.axs1[0].plot(frecuencias[:muestras // 2], magnitude2[:muestras // 2], 'magenta', label='CH2', linewidth=2)
            self.axs1[0].set_title("Espectro de Fourier (Magnitud)", fontweight='bold')
            self.axs1[0].set_xlabel("Frecuencia")
            self.axs1[0].set_ylabel("Magnitud")
            self.axs1[0].legend(loc='upper right')
            
            self.axs1[1].plot(frecuencias[:muestras // 2], real1[:muestras // 2], 'cyan', label='CH1 Real', linewidth=2)
            if self.usar_canal2.get():
                self.axs1[1].plot(frecuencias[:muestras // 2], real2[:muestras // 2], 'magenta', label='CH2 Real', linewidth=2)
            self.axs1[1].set_title("Parte Real de la Transformada de Fourier", fontweight='bold')
            self.axs1[1].set_xlabel("Frecuencia")
            self.axs1[1].set_ylabel("Valor Real")
            self.axs1[1].legend(loc='upper right')
            
            self.axs1[2].plot(frecuencias[:muestras // 2], imag1[:muestras // 2], 'cyan', label='CH1 Imaginario', linewidth=2)
            if self.usar_canal2.get():
                self.axs1[2].plot(frecuencias[:muestras // 2], imag2[:muestras // 2], 'magenta', label='CH2 Imaginario', linewidth=2)
            self.axs1[2].set_title("Parte Imaginaria de la Transformada de Fourier", fontweight='bold')
            self.axs1[2].set_xlabel("Frecuencia")
            self.axs1[2].set_ylabel("Valor Imaginario")
            self.axs1[2].legend(loc='upper right')
            
            self.fig1.tight_layout()
            
            # Ventana 2: Fase y Señales combinadas
            self.axs2[0].plot(frecuencias[:muestras // 2], phase1[:muestras // 2], 'cyan', label='CH1 Fase', linewidth=2)
            if self.usar_canal2.get():
                self.axs2[0].plot(frecuencias[:muestras // 2], phase2[:muestras // 2], 'magenta', label='CH2 Fase', linewidth=2)
            self.axs2[0].set_title("Fase (radianes)", fontweight='bold')
            self.axs2[0].set_xlabel("Frecuencia")
            self.axs2[0].set_ylabel("Fase (rad)")
            self.axs2[0].legend(loc='upper right')
            
            self.axs2[1].plot(t_anim, senal1, 'cyan', label='CH1', linewidth=2)
            if self.usar_canal2.get():
                self.axs2[1].plot(t_anim, senal2, 'magenta', label='CH2', linewidth=2)
            self.axs2[1].set_title("Señales combinadas (Tiempo)", fontweight='bold')
            self.axs2[1].set_xlabel("Índices (n)")
            self.axs2[1].set_ylabel("Amplitud")
            self.axs2[1].legend(loc='upper right')
            
            self.fig2.tight_layout()
            
            # Ventana 3: Preparar animación
            self.senal1 = senal1
            self.senal2 = senal2
            self.muestras = muestras
            self.t_anim = t_anim
            
            # Configurar ejes para la animación
            self.ax3.set_xlim(0, muestras)
            max_amp = max(self.senal1_vars['amplitud'].get(), 
                         self.senal2_vars['amplitud'].get() if self.usar_canal2.get() else 0, 
                         1)
            self.ax3.set_ylim(-max_amp * 1.5, max_amp * 1.5)
            self.ax3.set_title("Simulación de Osciloscopio (Animación)", fontweight='bold')
            self.ax3.set_xlabel("Índices (n)")
            self.ax3.set_ylabel("Amplitud")
            
            # Crear líneas iniciales para la animación (vacías)
            self.line1, = self.ax3.plot([], [], 'cyan', label='CH1', linewidth=2)
            if self.usar_canal2.get():
                self.line2, = self.ax3.plot([], [], 'magenta', label='CH2', linewidth=2)
                self.ax3.legend(loc='upper right')
            else:
                self.ax3.legend(loc='upper right')
            
            # Actualizar canvases
            self.canvas1.draw()
            self.canvas2.draw()
            self.canvas3.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")
    
    def start_animation(self):
        try:
            # Verificar que hay señales generadas
            if not hasattr(self, 'senal1'):
                messagebox.showwarning("Advertencia", "Primero debe generar las señales")
                return
            
            # Detener animación anterior si existe
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
            
            # Función de actualización para la animación
            def update(frame):
                shift = frame % self.muestras
                s1_shifted = np.roll(self.senal1, -shift)
                self.line1.set_data(self.t_anim, s1_shifted)
                
                if self.usar_canal2.get():
                    s2_shifted = np.roll(self.senal2, -shift)
                    self.line2.set_data(self.t_anim, s2_shifted)
                    return self.line1, self.line2
                else:
                    return self.line1,
            
            # Crear animación
            self.ani = FuncAnimation(self.fig3, update, frames=self.muestras, 
                                    interval=50, blit=True, repeat=True)
            
            # Actualizar canvas
            self.canvas3.draw()
            
            # Cambiar a la pestaña de osciloscopio
            self.notebook.select(2)
            
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error en la animación: {str(e)}")
    
    def clear_plots(self):
        # Limpiar gráficos
        for ax in self.axs1:
            ax.clear()
            ax.set_facecolor('#34495e')
            ax.grid(True, color='#4a6572', linestyle='--', linewidth=0.5)
        
        for ax in self.axs2:
            ax.clear()
            ax.set_facecolor('#34495e')
            ax.grid(True, color='#4a6572', linestyle='--', linewidth=0.5)
        
        self.ax3.clear()
        self.ax3.set_facecolor('#34495e')
        self.ax3.grid(True, color='#4a6572', linestyle='--', linewidth=0.5)
        
        # Limpiar líneas de animación
        self.line1 = None
        self.line2 = None
        
        # Actualizar canvases
        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()
        
        # Detener animación si existe
        if hasattr(self, 'ani'):
            self.ani.event_source.stop()
            del self.ani

def main():
    root = tk.Tk()
    app = SignalGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()