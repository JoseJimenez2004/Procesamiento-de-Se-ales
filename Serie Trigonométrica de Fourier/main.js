document.addEventListener('DOMContentLoaded', () => {
    // Variables globales para las instancias de las gráficas
    let originalChart = null;
    let fourierChart = null;

    // Configuración para manejar la selección de señal personalizada
    const signalSelect = document.getElementById('signal-select');
    const customCoefficientsDiv = document.getElementById('custom-coefficients');

    signalSelect.addEventListener('change', function() {
        if (this.value === 'custom') {
            customCoefficientsDiv.style.display = 'block';
        } else {
            customCoefficientsDiv.style.display = 'none';
        }
    });

    // Definimos las funciones para las señales originales
    function squareWave(t, T = 2 * Math.PI) {
        let t_mod = ((t + T / 2) % T + T) % T;
        return (t_mod < T / 2) ? 1 : -1;
    }

    function sawtoothWave(t, T = 2 * Math.PI) {
        let t_mod = ((t % T) + T) % T;
        return 2 * (t_mod / T) - 1;
    }

    function triangleWave(t, T = 2 * Math.PI) {
        let t_mod = ((t % T) + T) % T;
        let halfT = T / 2;
        if (t_mod < halfT) {
            return 2 * (t_mod / halfT) - 1;
        } else {
            return 1 - 2 * ((t_mod - halfT) / halfT);
        }
    }

    // Función para obtener los coeficientes según el tipo de señal
    function getCoefficients(signalType, nTerms) {
        const a0 = 0; // Para señales impares
        const an = new Array(nTerms).fill(0);
        const bn = new Array(nTerms).fill(0);

        switch (signalType) {
            case 'square':
                for (let n = 1; n <= nTerms; n++) {
                    if (n % 2 !== 0) {
                        bn[n-1] = 4 / (n * Math.PI);
                    }
                }
                break;
            case 'sawtooth':
                for (let n = 1; n <= nTerms; n++) {
                    bn[n-1] = 2 * Math.pow(-1, n+1) / (n * Math.PI);
                }
                break;
            case 'triangle':
                for (let n = 1; n <= nTerms; n++) {
                    if (n % 2 !== 0) {
                        bn[n-1] = 8 * Math.pow(-1, (n-1)/2) / (Math.pow(n, 2) * Math.PI * Math.PI);
                    }
                }
                break;
            case 'custom':
                // Leer coeficientes personalizados
                const customA0 = parseFloat(document.getElementById('a0-input').value) || 0;
                const customAn = document.getElementById('an-input').value.split(',').map(x => parseFloat(x.trim()) || 0);
                const customBn = document.getElementById('bn-input').value.split(',').map(x => parseFloat(x.trim()) || 0);
                
                return {
                    a0: customA0,
                    an: customAn,
                    bn: customBn
                };
        }

        return { a0, an, bn };
    }

    // Función para calcular la aproximación de Fourier
    function fourierApproximation(t, signalType, nTerms, T) {
        const coefficients = getCoefficients(signalType, nTerms);
        let sum = coefficients.a0 / 2;
        const omega = 2 * Math.PI / T;

        for (let n = 1; n <= nTerms; n++) {
            if (n-1 < coefficients.an.length) {
                sum += coefficients.an[n-1] * Math.cos(n * omega * t);
            }
            if (n-1 < coefficients.bn.length) {
                sum += coefficients.bn[n-1] * Math.sin(n * omega * t);
            }
        }
        return sum;
    }

    // Función para obtener la señal original
    function getOriginalSignal(t, signalType, T) {
        switch (signalType) {
            case 'square':
                return squareWave(t, T);
            case 'sawtooth':
                return sawtoothWave(t, T);
            case 'triangle':
                return triangleWave(t, T);
            case 'custom':
                // Para señal personalizada, mostramos la aproximación con muchos términos
                return fourierApproximation(t, 'custom', 50, T);
            default:
                return 0;
        }
    }

    // Función principal para actualizar las gráficas
    window.updateGraphs = function() {
        const signalType = document.getElementById('signal-select').value;
        const nTerms = parseInt(document.getElementById('n-input').value, 10);
        const T = parseFloat(document.getElementById('period-input').value);

        // Validaciones
        if (isNaN(nTerms) || nTerms < 1 || nTerms > 50) {
            alert("Por favor, introduce un número de términos válido (1 ≤ n ≤ 50).");
            return;
        }

        if (isNaN(T) || T <= 0) {
            alert("Por favor, introduce un período válido (T > 0).");
            return;
        }

        const labels = [];
        const originalData = [];
        const fourierData = [];

        const t_start = -T;
        const t_end = T;
        const t_step = T / 200;

        // Generamos los puntos para las gráficas
        for (let t = t_start; t <= t_end; t += t_step) {
            labels.push(t.toFixed(2));
            originalData.push(getOriginalSignal(t, signalType, T));
            fourierData.push(fourierApproximation(t, signalType, nTerms, T));
        }

        // Configuración común para las gráficas
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                x: {
                    title: { 
                        display: true, 
                        text: 'Tiempo (t)',
                        font: { size: 14, weight: 'bold' }
                    },
                    grid: { color: 'rgba(0,0,0,0.1)' }
                },
                y: {
                    title: { 
                        display: true, 
                        text: 'Amplitud',
                        font: { size: 14, weight: 'bold' }
                    },
                    grid: { color: 'rgba(0,0,0,0.1)' },
                    suggestedMin: -1.5,
                    suggestedMax: 1.5
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: { size: 12 }
                    }
                }
            }
        };

        // Configuración de la gráfica de la señal original
        const originalConfig = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Señal Original (${signalType})`,
                    data: originalData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 3,
                    tension: 0.1,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: commonOptions
        };

        // Configuración de la gráfica de la aproximación de Fourier
        const fourierConfig = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Aproximación de Fourier (n=${nTerms})`,
                    data: fourierData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 3,
                    tension: 0.1,
                    pointRadius: 0,
                    fill: true
                }]
            },
            options: commonOptions
        };

        // Destruimos las instancias previas de las gráficas
        if (originalChart) originalChart.destroy();
        if (fourierChart) fourierChart.destroy();

        // Creamos las nuevas gráficas
        const ctxOriginal = document.getElementById('original-chart').getContext('2d');
        originalChart = new Chart(ctxOriginal, originalConfig);

        const ctxFourier = document.getElementById('fourier-chart').getContext('2d');
        fourierChart = new Chart(ctxFourier, fourierConfig);

        // Mostrar información de coeficientes en consola
        if (signalType !== 'custom') {
            const coefficients = getCoefficients(signalType, nTerms);
            console.log('Coeficientes calculados:');
            console.log('a₀ =', coefficients.a0);
            console.log('aₙ =', coefficients.an);
            console.log('bₙ =', coefficients.bn);
        }
    };

    // Inicializar la aplicación
    updateGraphs();
});