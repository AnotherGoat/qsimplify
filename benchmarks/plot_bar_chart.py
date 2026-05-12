import json
import matplotlib.pyplot as plt
import numpy as np
import os

with open('benchmarks/benchmark_results.json', 'r') as f:
    data = json.load(f)

results = {}

for b in data['benchmarks']:
    name = b['name'].split('[')[0].replace('test_', '').replace('_', ' ').title()
    qubits = int(b['param'])
    time = b['stats']['mean']
    
    if name not in results:
        results[name] = {}
    results[name][qubits] = time

# Preparar datos para el gráfico de barras
labels = ['1 Qubit', '2 Qubits', '4 Qubits', '8 Qubits']
qubit_vals = [1, 2, 4, 8]

# Extraer tiempos por algoritmo
algos = list(results.keys())
times_per_algo = []
for algo in algos:
    # Si no hay dato para un qubit (ej. CNOT en 1 qubit), ponemos 0
    times = [results[algo].get(q, 0) for q in qubit_vals]
    times_per_algo.append(times)

x = np.arange(len(labels))  # Localización de las etiquetas
width = 0.25  # Ancho de las barras

fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')

colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

# Crear barras agrupadas
for i, algo in enumerate(algos):
    # Desplazar cada grupo de barras
    offset = width * i - width
    ax.bar(x + offset, times_per_algo[i], width, label=algo, color=colors[i], edgecolor='black')

# Línea roja de límite
ax.axhline(y=300, color='red', linestyle='--', linewidth=2, label='Límite Crítico (5 min)')

ax.set_ylim(0, 315)

# Añadir etiquetas y títulos
ax.set_ylabel('Tiempo en Segundos (Mientras más alto, peor)', fontsize=12)
ax.set_title('Comparación Directa de Tiempos por Algoritmo', fontsize=16, pad=20)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=12)

# Leyenda fuera del gráfico, en la parte inferior central
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2, fontsize=11)

# Poner cuadrícula solo horizontal para guiar el ojo
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()

os.makedirs('benchmarks', exist_ok=True)
plt.savefig('benchmarks/grafico_barras_simple.png', dpi=300, bbox_inches='tight')
print("Gráfico de barras generado con éxito.")
