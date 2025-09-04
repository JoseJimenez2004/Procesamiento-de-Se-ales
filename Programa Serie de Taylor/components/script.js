let chart = null;
let fourierSeries = null;
let originalFunction = null;
let period = 2;

// Elementos DOM
const simpleFunctionBtn = document.getElementById('simple-function-btn');
const piecewiseFunctionBtn = document.getElementById('piecewise-function-btn');
const simpleFunctionContainer = document.getElementById('simple-function-container');
const piecewiseFunctionContainer = document.getElementById('piecewise-function-container');
const calculateBtn = document.getElementById('calculate-btn');
const nTermsInput = document.getElementById('n-terms');
const nValueDisplay = document.getElementById('n-value');
const resultsContainer = document.getElementById('results');
const coefficientsOutput = document.getElementById('coefficients-output');
const fourierSeriesDisplay = document.getElementById('fourier-series');
const seriesTermsInput = document.getElementById('series-terms');
const sliderValueDisplay = document.getElementById('slider-value');
const periodInput = document.getElementById('period');
const functionPartsContainer = document.getElementById('function-parts');
const addPartBtn = document.getElementById('add-part');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    simpleFunctionBtn.addEventListener('click', () => toggleFunctionType('simple'));
    piecewiseFunctionBtn.addEventListener('click', () => toggleFunctionType('piecewise'));

    nTermsInput.addEventListener('input', function() {
        nValueDisplay.textContent = this.value;
    });

    seriesTermsInput.addEventListener('input', function() {
        sliderValueDisplay.textContent = this.value;
        if(fourierSeries) updateChart(parseInt(this.value));
    });

    calculateBtn.addEventListener('click', calculateFourierSeries);
    addPartBtn.addEventListener('click', addFunctionPart);

    functionPartsContainer.addEventListener('click', function(e) {
        if(e.target.classList.contains('remove-part') && functionPartsContainer.children.length>1) {
            e.target.closest('.function-part').remove();
        }
    });

    initChart();
});

// Funciones principales
function toggleFunctionType(type){
    if(type==='simple'){
        simpleFunctionBtn.classList.replace('btn-secondary','btn-primary');
        piecewiseFunctionBtn.classList.replace('btn-primary','btn-secondary');
        simpleFunctionContainer.classList.remove('hidden');
        piecewiseFunctionContainer.classList.add('hidden');
    } else {
        piecewiseFunctionBtn.classList.replace('btn-secondary','btn-primary');
        simpleFunctionBtn.classList.replace('btn-primary','btn-secondary');
        piecewiseFunctionContainer.classList.remove('hidden');
        simpleFunctionContainer.classList.add('hidden');
    }
}

function addFunctionPart() {
    const newPart = document.createElement('div');
    newPart.className = 'function-part bg-gray-50 p-4 rounded-lg border border-gray-200';
    const index = functionPartsContainer.children.length;
    newPart.innerHTML = `
        <div class="grid grid-cols-3 gap-4 mb-2">
            <div>
                <label class="block text-gray-700 text-sm mb-1">Desde</label>
                <input type="number" value="${index}" class="w-full px-2 py-1 border border-gray-300 rounded">
            </div>
            <div>
                <label class="block text-gray-700 text-sm mb-1">Hasta</label>
                <input type="number" value="${index+1}" class="w-full px-2 py-1 border border-gray-300 rounded">
            </div>
            <div class="flex items-end">
                <button class="remove-part px-2 py-1 bg-red-500 text-white rounded text-sm">Eliminar</button>
            </div>
        </div>
        <input type="text" value="0" class="w-full px-2 py-1 border border-gray-300 rounded" placeholder="Función para este intervalo">
    `;
    functionPartsContainer.appendChild(newPart);
}

// Inicializar gráfico
function initChart(){
    const ctx = document.getElementById('function-chart').getContext('2d');

    const gradientOriginal = ctx.createLinearGradient(0,0,0,400);
    gradientOriginal.addColorStop(0,'rgba(0,123,255,0.5)');
    gradientOriginal.addColorStop(1,'rgba(0,123,255,0.1)');

    const gradientFourier = ctx.createLinearGradient(0,0,0,400);
    gradientFourier.addColorStop(0,'rgba(0, 255, 149, 0.92)');
    gradientFourier.addColorStop(1,'rgba(139,92,246,0.1)');

    chart = new Chart(ctx,{
        type:'line',
        data:{
            datasets:[
                { label:'Función original', borderColor:'#2563eb', backgroundColor:gradientOriginal, borderWidth:3, pointRadius:0, fill:true, tension:0.3 },
                { label:'Aproximación de Fourier', borderColor:'#5cf68aff', backgroundColor:gradientFourier, borderWidth:3, pointRadius:0, fill:true, tension:0.3 }
            ]
        },
        options:{
            responsive:true,
            maintainAspectRatio:false,
            plugins:{
                legend:{ labels:{ color:'#374151', font:{size:14, weight:'bold'} } },
                tooltip:{
                    backgroundColor:'rgba(31,41,55,0.9)',
                    titleColor:'#fff', bodyColor:'#f9fafb',
                    borderColor:'#5cf68aff', borderWidth:1,
                    padding:10, cornerRadius:10
                }
            },
            scales:{
                x:{ type:'linear', position:'bottom', title:{ display:true, text:'t', color:'#374151', font:{size:14, weight:'bold'}}, grid:{ color:'rgba(0,0,0,0.05)'} },
                y:{ title:{ display:true, text:'f(t)', color:'#374151', font:{size:14, weight:'bold'}}, grid:{ color:'rgba(0,0,0,0.05)'} }
            },
            animation:{ duration:1200, easing:'easeOutQuart' }
        },
        plugins:[{
            beforeDraw: chart=>{ const ctx=chart.ctx; ctx.save(); ctx.shadowColor='rgba(0,0,0,0.2)'; ctx.shadowBlur=10; ctx.shadowOffsetX=2; ctx.shadowOffsetY=4; },
            afterDraw: chart=>{ chart.ctx.restore(); }
        }]
    });
}

// Calcular Serie de Fourier
function calculateFourierSeries(){
    period=parseFloat(periodInput.value);
    const n=parseInt(nTermsInput.value);
    let functionType = simpleFunctionContainer.classList.contains('hidden')?'piecewise':'simple';

    try {
        if(functionType==='simple'){
            const expr=document.getElementById('function-input').value;
            originalFunction = t=> math.evaluate(expr,{t});
        } else {
            const parts=[];
            const partElements = functionPartsContainer.querySelectorAll('.function-part');
            partElements.forEach(partEl=>{
                const inputs = partEl.querySelectorAll('input');
                parts.push({
                    from:parseFloat(inputs[0].value),
                    to:parseFloat(inputs[1].value),
                    func: t => math.evaluate(inputs[2].value,{t})
                });
            });
            originalFunction = t=>{
                const adjustedT = t%period;
                for(const part of parts) if(adjustedT>=part.from && adjustedT<=part.to) return part.func(adjustedT);
                return 0;
            };
        }

        const coefficients = calculateCoefficients(originalFunction, period, n);

        fourierSeries = t=>{
            let result = coefficients.a0/2;
            for(let i=1;i<=n;i++){
                result += coefficients.an[i]*Math.cos(i*2*Math.PI*t/period);
                result += coefficients.bn[i]*Math.sin(i*2*Math.PI*t/period);
            }
            return result;
        };

        displayResults(coefficients,n);
        updateChart(n);
    } catch(e){
        alert(`Error: ${e.message}`);
        console.error(e);
    }
}

// Cálculo de coeficientes
function calculateCoefficients(func, period, n){
    const integrationPoints=1000;
    const coefficients={a0:0, an:{}, bn:{}};
    let sum=0;
    for(let i=0;i<integrationPoints;i++){
        const t=i*period/integrationPoints;
        sum+=func(t);
    }
    coefficients.a0=2*sum/integrationPoints;

    for(let k=1;k<=n;k++){
        let sumAn=0,sumBn=0;
        const omega=2*Math.PI*k/period;
        for(let i=0;i<integrationPoints;i++){
            const t=i*period/integrationPoints;
            const val=func(t);
            sumAn += val*Math.cos(omega*t);
            sumBn += val*Math.sin(omega*t);
        }
        coefficients.an[k]=2*sumAn/integrationPoints;
        coefficients.bn[k]=2*sumBn/integrationPoints;
    }

    return coefficients;
}

// Mostrar resultados
function displayResults(coefficients,n){
    let output=`a0=${coefficients.a0.toFixed(4)}\n`;
    for(let i=1;i<=n;i++) output+=`a${i}=${coefficients.an[i].toFixed(4)}, b${i}=${coefficients.bn[i].toFixed(4)}\n`;
    coefficientsOutput.textContent=output;

    let seriesText=`f(t) ≈ ${(coefficients.a0/2).toFixed(4)} `;
    for(let i=1;i<=n;i++){
        const an=coefficients.an[i], bn=coefficients.bn[i];
        if(Math.abs(an)>1e-4) seriesText += `${an>=0?'+':'-'} ${Math.abs(an).toFixed(4)} cos(${i}ωt) `;
        if(Math.abs(bn)>1e-4) seriesText += `${bn>=0?'+':'-'} ${Math.abs(bn).toFixed(4)} sin(${i}ωt) `;
    }
    fourierSeriesDisplay.textContent=seriesText;
    resultsContainer.style.display='block';
}

// Actualizar gráfica
function updateChart(n){
    if(!originalFunction || !fourierSeries) return;
    const points=200;
    const originalData=[], fourierData=[];
    const start=0, end=2*period;
    for(let i=0;i<points;i++){
        const t=start+(end-start)*i/points;
        originalData.push({x:t,y:originalFunction(t)});
        fourierData.push({x:t,y:fourierSeries(t)});
    }
    chart.data.datasets[0].data=originalData;
    chart.data.datasets[1].data=fourierData;
    chart.update();
}
