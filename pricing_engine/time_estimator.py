from collections import defaultdict
from typing import Any

from pricing_engine.estimator_models import BackendProfile
from qsimplify.model import GateName
from qsimplify.model.quantum_gate import QuantumGate, parse_gates


def get_gate_cost(gate: QuantumGate, profile: BackendProfile) -> float:
    """Returns the cost of a gate according to the backend profile."""
    # Phase / Rz gates
    if gate.name in (GateName.P, GateName.RZ, GateName.ID):
        return profile.phase_cost
        
    # Sqrt gates
    if gate.name in (GateName.SX, GateName.SY):
        return profile.sqrt_cost
        
    # Single qubit gates
    if gate.name in (
        GateName.X, GateName.Y, GateName.Z, GateName.RX, GateName.RY, 
        GateName.H, GateName.S, GateName.SDG, GateName.T, GateName.TDG
    ):
        return profile.single_qubit_cost
        
    # Measure
    if gate.name == GateName.MEASURE:
        return profile.measure_cost
        
    # Swap
    if gate.name == GateName.SWAP:
        return profile.swap_cost
        
    # Two qubit gates
    if gate.name in (GateName.CX, GateName.CY, GateName.CZ, GateName.CH, GateName.CP):
        return profile.two_qubit_cost
        
    # Three qubit gates
    if gate.name in (GateName.CCX, GateName.CCZ, GateName.CSWAP):
        return profile.three_qubit_cost
    
        
    # Default to single qubit cost if not found
    return profile.single_qubit_cost


def get_gate_qubits(gate: QuantumGate) -> list[int]:
    """Returns all qubits affected by a given gate."""
    qubits = []
    # Usamos getattr en lugar de hasattr y acceso directo para evitar 
    # que el linter (basedpyright) se queje de atributos inexistentes.
    attributes = [
        "qubit", "qubit2", "qubit3", 
        "control_qubit", "control_qubit2", 
        "target_qubit", "target_qubit2"
    ]
    for attr in attributes:
        val = getattr(gate, attr, None)
        if val is not None:
            qubits.append(val)
    return qubits


def estimate_execution_time(gates_json: list[dict[str, Any]], shots: int, profile: BackendProfile) -> float:
    """
    Estimates the total execution time of a circuit using critical path algorithm.
    """
    gates = parse_gates(gates_json)
    
    # Track the accumulated time for each qubit
    qubit_times: dict[int, float] = defaultdict(float)
    
    for gate in gates:
        qubits = get_gate_qubits(gate)
        if not qubits:
            continue
            
        gate_cost = get_gate_cost(gate, profile)
        
        # The gate starts when all involved qubits are ready
        start_time = max(qubit_times[q] for q in qubits)
        end_time = start_time + gate_cost
        
        # Update the time for all involved qubits
        for q in qubits:
            qubit_times[q] = end_time
            
    # The critical path is the maximum time among all qubits
    critical_path_time = max(qubit_times.values()) if qubit_times else 0.0
    
    # Calculate the final heuristic time
    total_time = shots * (critical_path_time + profile.repetition_delay_cost)
    
    return total_time
