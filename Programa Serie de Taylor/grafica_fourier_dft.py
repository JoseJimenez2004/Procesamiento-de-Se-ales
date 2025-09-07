import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import square, sawtooth

def generar_senal(tipo, frecuencia, muestras, amplitud, continua):
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

# canal1
print("Canal 1 (CH1):")
print("1. Senoidal\n2. Cuadrada\n3. Triangular")
op1 = int(input("Seleccione el tipo de señal: "))
freq1 = float(input("Ingrese frecuencia (Hz): "))
amp1 = float(input("Ingrese amplitud: "))
muestras1 = int(input("Número de muestras: "))
cont1 = input("¿Es señal continua? (s/n): ").lower() == 's'
tipo1 = {1: "seno", 2: "cuadrada", 3: "triangular"}.get(op1, "seno")
t1, senal1 = generar_senal(tipo1, freq1, muestras1, amp1, cont1)


usar_canal2 = input("\n¿Desea usar el segundo canal? (s/n): ").lower()
if usar_canal2 == 's':
    print("\nCanal 2 (CH2):")
    print("1. Senoidal\n2. Cuadrada\n3. Triangular")
    op2 = int(input("Seleccione el tipo de señal: "))
    freq2 = float(input("Ingrese frecuencia (Hz): "))
    amp2 = float(input("Ingrese amplitud: "))
    muestras2 = int(input("Número de muestras: "))
    cont2 = input("¿Es señal continua? (s/n): ").lower() == 's'
    tipo2 = {1: "seno", 2: "cuadrada", 3: "triangular"}.get(op2, "seno")
    t2, senal2 = generar_senal(tipo2, freq2, muestras2, amp2, cont2)
else:
    muestras2 = muestras1
    amp2 = 0
    cont2 = cont1
    t2 = t1
    senal2 = np.zeros(muestras2)

# --- Ajuste para mismo tamaño ---
muestras = max(muestras1, muestras2)
if len(senal1) < muestras:
    senal1 = np.pad(senal1, (0, muestras - len(senal1)))
if len(senal2) < muestras:
    senal2 = np.pad(senal2, (0, muestras - len(senal2)))

t_anim = np.arange(muestras)

# --- Calcular FFT ---
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

# Ventana 1: Espectro, Real, Imaginario 
fig1, axs1 = plt.subplots(3, 1, figsize=(12, 12))
plt.subplots_adjust(hspace=0.6)

axs1[0].plot(frecuencias[:muestras // 2], magnitude1[:muestras // 2], 'b', label='CH1')
if usar_canal2 == 's':
    axs1[0].plot(frecuencias[:muestras // 2], magnitude2[:muestras // 2], 'r', label='CH2')
axs1[0].set_title("Espectro de Fourier (Magnitud)", fontsize=12)
axs1[0].set_xlabel("Frecuencia", fontsize=10)
axs1[0].set_ylabel("Magnitud", fontsize=10)
axs1[0].legend(loc='upper right')
axs1[0].grid(True)

axs1[1].plot(frecuencias[:muestras // 2], real1[:muestras // 2], 'b', label='CH1 Real')
if usar_canal2 == 's':
    axs1[1].plot(frecuencias[:muestras // 2], real2[:muestras // 2], 'r', label='CH2 Real')
axs1[1].set_title("Parte Real de la Transformada de Fourier", fontsize=12)
axs1[1].set_xlabel("Frecuencia", fontsize=10)
axs1[1].set_ylabel("Valor Real", fontsize=10)
axs1[1].legend(loc='upper right')
axs1[1].grid(True)

axs1[2].plot(frecuencias[:muestras // 2], imag1[:muestras // 2], 'b', label='CH1 Imaginario')
if usar_canal2 == 's':
    axs1[2].plot(frecuencias[:muestras // 2], imag2[:muestras // 2], 'r', label='CH2 Imaginario')
axs1[2].set_title("Parte Imaginaria de la Transformada de Fourier", fontsize=12)
axs1[2].set_xlabel("Frecuencia", fontsize=10)
axs1[2].set_ylabel("Valor Imaginario", fontsize=10)
axs1[2].legend(loc='upper right')
axs1[2].grid(True)

plt.tight_layout()
plt.show(block=False)

# Ventana 2: Fase y Señales combinadas 
fig2, axs2 = plt.subplots(2, 1, figsize=(12, 8))
plt.subplots_adjust(hspace=0.5)

axs2[0].plot(frecuencias[:muestras // 2], phase1[:muestras // 2], 'b', label='CH1 Fase')
if usar_canal2 == 's':
    axs2[0].plot(frecuencias[:muestras // 2], phase2[:muestras // 2], 'r', label='CH2 Fase')
axs2[0].set_title("Fase (radianes)", fontsize=12)
axs2[0].set_xlabel("Frecuencia", fontsize=10)
axs2[0].set_ylabel("Fase (rad)", fontsize=10)
axs2[0].legend(loc='upper right')
axs2[0].grid(True)

axs2[1].plot(t_anim, senal1, 'b-', label='CH1')
if usar_canal2 == 's':
    axs2[1].plot(t_anim, senal2, 'r-', label='CH2')
axs2[1].set_title("Señales combinadas (Tiempo)", fontsize=12)
axs2[1].set_xlabel("Índices (n)", fontsize=10)
axs2[1].set_ylabel("Amplitud", fontsize=10)
axs2[1].legend(loc='upper right')
axs2[1].grid(True)

plt.tight_layout()
plt.show(block=False)

# Ventana 3: Animación Osciloscopio 
fig3, ax3 = plt.subplots(figsize=(12, 4))
line1, = ax3.plot([], [], 'b-', label='CH1 (Azul)')
if usar_canal2 == 's':
    line2, = ax3.plot([], [], 'r-', label='CH2 (Rojo)')
ax3.set_xlim(0, muestras)
ax3.set_ylim(-max(amp1, amp2, 1) * 1.5, max(amp1, amp2, 1) * 1.5)
ax3.set_title("Simulación de Osciloscopio (Animación)", fontsize=12)
ax3.set_xlabel("Índices (n)", fontsize=10)
ax3.set_ylabel("Amplitud", fontsize=10)
ax3.legend(loc='upper right')
ax3.grid(True)

def update(frame):
    shift = frame % muestras
    s1_shifted = np.roll(senal1, -shift)
    line1.set_data(t_anim, s1_shifted)
    if usar_canal2 == 's':
        s2_shifted = np.roll(senal2, -shift)
        line2.set_data(t_anim, s2_shifted)
        return line1, line2
    else:
        return line1,

ani = FuncAnimation(fig3, update, frames=np.arange(0, muestras), interval=50, blit=True)
plt.show()
