import os
import qiskit

os.makedirs('benchmarks', exist_ok=True)

# Caso 1: Cadenas de anulación
qc1 = qiskit.QuantumCircuit(1)
qc1.h(0)
qc1.h(0)
qc1.h(0)
qc1.h(0)
qc1.draw(output='mpl', filename='benchmarks/caso1_cancellation_chain.png')

# Caso 2: Cascada CNOT
qc2 = qiskit.QuantumCircuit(3)
qc2.cx(0, 1)
qc2.cx(1, 2)
qc2.cx(1, 2)
qc2.cx(0, 1)
qc2.draw(output='mpl', filename='benchmarks/caso2_cnot_cascade.png')

# Caso 3: Muro de ladrillos
qc3 = qiskit.QuantumCircuit(2)
qc3.h(0)
qc3.t(0)
qc3.cx(0, 1)
qc3.s(0)
qc3.h(1)
qc3.t(1)
qc3.s(1)
qc3.draw(output='mpl', filename='benchmarks/caso3_brick_wall.png')

print("¡Imágenes generadas con éxito en la carpeta docs/!")
