import logging

from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations

_debug_mode = False

def set_debug_mode(debug):
    global _debug_mode
    _debug_mode = debug


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def find_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    qubits = []

    for qubit in instruction.qubits:
        bit_locations: BitLocations = circuit.find_bit(qubit)

        for (_, qubit_index) in bit_locations.registers:
            qubits.append(qubit_index)

    return qubits

def find_bit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    bits = []

    for bit in instruction.clbits:
        bit_locations: BitLocations = circuit.find_bit(bit)

        for (_, bit_index) in bit_locations.registers:
            bits.append(bit_index)

    return bits
