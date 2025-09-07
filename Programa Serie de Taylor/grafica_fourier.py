import numpy as np
import matplotlib.pyplot as plt

# Pedir datos al usuario
frecuencia = float(input("Ingrese la frecuencia de la señal (Hz): "))
muestras = int(input("Ingrese el número de muestras: "))

# Generar señal en el dominio del tiempo
t = np.linspace(0, 1, muestras)
senal = np.sin(2 * np.pi * frecuencia * t)

# Calcular Transformada de Fourier
frecuencia_fft = np.fft.fftfreq(muestras, d=(t[1] - t[0]))
amplitud_fft = np.abs(np.fft.fft(senal))

# Graficar señal en el tiempo
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(t, senal)
plt.title("Señal en el dominio del tiempo")
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")

# Graficar Transformada de Fourier
plt.subplot(2, 1, 2)
plt.plot(frecuencia_fft[:muestras//2], amplitud_fft[:muestras//2])
plt.title("Transformada de Fourier")
plt.xlabel("Frecuencia (Hz)")
plt.ylabel("Amplitud")

plt.tight_layout()
plt.show()
