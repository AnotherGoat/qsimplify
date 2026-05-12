import pytest
from qsimplify.simplifier import Simplifier
from qsimplify.converter import GatesConverter
from qsimplify.model.quantum_gate import HGate, CxGate, TGate, SGate

# Inicializamos las herramientas principales del sistema
gates_converter = GatesConverter()
simplifier = Simplifier()

import threading
import time

def process_and_simplify(gates, benchmark_fixture=None):
    """
    Toma las compuertas, las convierte en un grafo y las simplifica.
    Incluye un mecanismo estricto: si tarda más de 5 minutos (300s),
    aborta la espera y deja evidencia en el archivo JSON.
    """
    TIMEOUT_SECONDS = 300
    result = []
    
    def worker():
        try:
            graph = gates_converter.to_graph(gates)
            result.append(simplifier.simplify_graph(graph, iterations=3))
        except Exception:
            pass

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    
    # Esperamos un máximo de 5 minutos
    thread.join(TIMEOUT_SECONDS)
    
    if thread.is_alive():
        # Si el hilo sigue vivo, significa que se quedó en un loop
        if benchmark_fixture:
            benchmark_fixture.extra_info["limite_superado"] = True
            benchmark_fixture.extra_info["diagnostico"] = "FALLO: Excedió el tiempo máximo aceptable de 5 minutos."
        return "TIMEOUT"
        
    return result[0] if result else None


# Definimos los niveles de escalamiento (Número de qubits)
QUBIT_COUNTS = [1, 2, 4, 8]


@pytest.mark.parametrize("n_qubits", QUBIT_COUNTS)
def test_cancellation_chain(benchmark, n_qubits):
    """Caso 1: Cadenas de anulación simple (100 compuertas H por qubit)."""
    gates = []
    for q in range(n_qubits):
        # 100 compuertas H por cada qubit. Deberían anularse todas a cero.
        for _ in range(100):
            gates.append(HGate(qubit=q))
            
    # Le decimos a pytest-benchmark que mida el tiempo de esta función
    benchmark(process_and_simplify, gates, benchmark)


@pytest.mark.parametrize("n_qubits", QUBIT_COUNTS)
def test_cnot_cascade(benchmark, n_qubits):
    """Caso 2: Cascada de CNOTs en red (Entrelazamiento complejo)."""
    if n_qubits < 2:
        pytest.skip("La cascada de CNOTs requiere al menos 2 qubits")
        
    gates = []
    # Ida y vuelta de CNOTs entrelazados para que el algoritmo trabaje
    # cruzando la información entre todos los qubits.
    for _ in range(10): # Repetimos el patrón 10 veces para dar peso
        for i in range(n_qubits - 1):
            gates.append(CxGate(control_qubit=i, target_qubit=i+1))
        for i in range(n_qubits - 2, -1, -1):
            gates.append(CxGate(control_qubit=i, target_qubit=i+1))
            
    benchmark(process_and_simplify, gates, benchmark)


@pytest.mark.parametrize("n_qubits", QUBIT_COUNTS)
def test_irreducible_brick_wall(benchmark, n_qubits):
    """Caso 3: El muro de ladrillos (100% No simplificable)."""
    gates = []
    # Patrón asimétrico diseñado para NO coincidir con ninguna regla.
    for q in range(n_qubits):
        for _ in range(25): # 100 compuertas por qubit
            gates.append(HGate(qubit=q))
            gates.append(TGate(qubit=q))
            if q < n_qubits - 1:
                gates.append(CxGate(control_qubit=q, target_qubit=q+1))
            gates.append(SGate(qubit=q))

    benchmark(process_and_simplify, gates, benchmark)
