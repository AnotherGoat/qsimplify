import logging
from logging import StreamHandler

from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations

_debug_mode = False
_handler: StreamHandler

def set_debug_mode(debug):
    global _debug_mode
    _debug_mode = debug

    global _handler
    _handler = logging.StreamHandler()
    _handler.setLevel(logging.DEBUG if _debug_mode else logging.INFO)

    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    _handler.setFormatter(formatter)


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if _debug_mode else logging.INFO)
    logger.addHandler(_handler)
    return logger


def get_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    qubits = []

    for qubit in instruction.qubits:
        bit_locations: BitLocations = circuit.find_bit(qubit)
        (_, qubit_index) = bit_locations.registers[0]
        qubits.append(qubit_index)

    return qubits
