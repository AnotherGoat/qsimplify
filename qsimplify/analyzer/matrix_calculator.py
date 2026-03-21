"""Contains unitary matrix calculations for quantum graphs."""

import numpy

from qsimplify.converter.gates_converter import GatesConverter
from qsimplify.model import GateName, QuantumGraph
from qsimplify.model.quantum_gate import QuantumGate

_GATES_CONVERTER = GatesConverter()


def are_graphs_equivalent(graph: QuantumGraph, graph2: QuantumGraph) -> bool:
    """Check whether the unitary matrices of two quantum graphs are equivalent by normalizing global phase.

    This uses numpy's default tolerance values.
    """
    return _are_matrices_equivalent(circuit_matrix(graph), circuit_matrix(graph2))


def _are_matrices_equivalent(unitary: numpy.ndarray, unitary2: numpy.ndarray) -> bool:
    phase = unitary.flat[0] / unitary2.flat[0] if unitary2.flat[0] != 0 else 1
    return numpy.allclose(unitary, phase * unitary2)


def circuit_matrix(graph: QuantumGraph) -> numpy.ndarray:
    """Get the matrix representation of the circuit represented by the graph.

    Measurement gates are ignored.
    """
    height = graph.height

    if graph.is_empty():
        return numpy.eye(2**height, dtype=complex)

    result = numpy.eye(2**height, dtype=complex)

    gates = _GATES_CONVERTER.from_graph(graph)

    for gate in gates:
        unitary_column = _gate_to_matrix(gate, height)
        result = unitary_column @ result

    return result


def _gate_to_matrix(gate: QuantumGate, height: int) -> numpy.ndarray:
    name = gate.name

    if name in _STATIC_GATES:
        return _embed_single(height, gate.qubit, _STATIC_GATES[name])

    if name in _PARAMETRIC_GATES:
        return _embed_single(height, gate.qubit, _PARAMETRIC_GATES[name](gate.angle))

    if name == GateName.SWAP:
        return _swap_gate(height, gate.qubit, gate.qubit2)

    if name == GateName.CX:
        return _control_gate(height, [gate.control_qubit], gate.target_qubit, _X)

    if name == GateName.CY:
        return _control_gate(height, [gate.control_qubit], gate.target_qubit, _Y)

    if name == GateName.CZ:
        return _control_gate(height, [gate.qubit], gate.qubit2, _Z)

    if name == GateName.CH:
        return _control_gate(height, [gate.control_qubit], gate.target_qubit, _H)

    if name == GateName.CP:
        return _control_gate(
            height,
            [gate.control_qubit],
            gate.target_qubit,
            _phase(gate.angle),
        )

    if name == GateName.CCX:
        return _control_gate(
            height,
            [gate.control_qubit, gate.control_qubit2],
            gate.target_qubit,
            _X,
        )

    if name == GateName.CCZ:
        return _control_gate(
            height,
            [gate.qubit, gate.qubit2],
            gate.qubit3,
            _Z,
        )

    if name == GateName.CSWAP:
        return _control_swap(
            height,
            gate.control_qubit,
            gate.target_qubit,
            gate.target_qubit2,
        )

    raise NotImplementedError(name)


def _embed_single(n: int, qubit: int, base: numpy.ndarray) -> numpy.ndarray:
    result = numpy.eye(1, dtype=complex)

    for i in range(n):
        if i == qubit:
            result = numpy.kron(result, base)
        else:
            result = numpy.kron(result, numpy.eye(2, dtype=complex))

    return result


def _gate_matrix(gate: GateName, angle: float | None = None) -> numpy.ndarray:
    if gate in _STATIC_GATES:
        return _STATIC_GATES[gate]

    if gate in _PARAMETRIC_GATES:
        if angle is None:
            raise ValueError(f"{gate} requires an angle")
        return _PARAMETRIC_GATES[gate](angle)

    raise NotImplementedError(f"Matrix not implemented for {gate}")


_I = numpy.eye(2, dtype=complex)

_H = (1 / numpy.sqrt(2)) * numpy.array([[1, 1], [1, -1]], dtype=complex)

_X = numpy.array([[0, 1], [1, 0]], dtype=complex)

_Y = numpy.array([[0, -1j], [1j, 0]], dtype=complex)

_Z = numpy.array([[1, 0], [0, -1]], dtype=complex)

_S = numpy.array([[1, 0], [0, 1j]], dtype=complex)

_SDG = numpy.array([[1, 0], [0, -1j]], dtype=complex)

_SX = 0.5 * numpy.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex)

_SY = 0.5 * numpy.array([[1 + 1j, -1 - 1j], [1 + 1j, 1 + 1j]], dtype=complex)

_T = numpy.array([[1, 0], [0, numpy.exp(1j * numpy.pi / 4)]], dtype=complex)

_TDG = numpy.array([[1, 0], [0, numpy.exp(-1j * numpy.pi / 4)]], dtype=complex)


_STATIC_GATES = {
    GateName.ID: _I,
    GateName.H: _H,
    GateName.X: _X,
    GateName.Y: _Y,
    GateName.Z: _Z,
    GateName.S: _S,
    GateName.SDG: _SDG,
    GateName.SX: _SX,
    GateName.SY: _SY,
    GateName.T: _T,
    GateName.TDG: _TDG,
    GateName.MEASURE: _I,
}


def _phase(angle: float) -> numpy.ndarray:
    return numpy.array([[1, 0], [0, numpy.exp(1j * angle)]], dtype=complex)


def _rx(angle: float) -> numpy.ndarray:
    return numpy.array(
        [
            [numpy.cos(angle / 2), -1j * numpy.sin(angle / 2)],
            [-1j * numpy.sin(angle / 2), numpy.cos(angle / 2)],
        ],
        dtype=complex,
    )


def _ry(angle: float) -> numpy.ndarray:
    return numpy.array(
        [
            [numpy.cos(angle / 2), -numpy.sin(angle / 2)],
            [numpy.sin(angle / 2), numpy.cos(angle / 2)],
        ],
        dtype=complex,
    )


def _rz(angle: float) -> numpy.ndarray:
    return numpy.array(
        [[numpy.exp(-1j * angle / 2), 0], [0, numpy.exp(1j * angle / 2)]], dtype=complex
    )


_PARAMETRIC_GATES = {
    GateName.P: _phase,
    GateName.RX: _rx,
    GateName.RY: _ry,
    GateName.RZ: _rz,
}


def _control_gate(
    height: int, controls: list[int], target: int, base_matrix: numpy.ndarray
) -> numpy.ndarray:
    size = 2**height
    unitary = numpy.zeros((size, size), dtype=complex)

    for index in range(size):
        bits = list(map(int, format(index, f"0{height}b")))

        if all(bits[control] == 1 for control in controls):
            t = bits[target]

            for new_t in [0, 1]:
                bits2 = bits.copy()
                bits2[target] = new_t
                j = int("".join(map(str, bits2)), 2)
                unitary[j, index] = base_matrix[new_t, t]
        else:
            unitary[index, index] = 1

    return unitary


def _swap_gate(height: int, qubit: int, qubit2: int) -> numpy.ndarray:
    size = 2**height
    unitary = numpy.zeros((size, size), dtype=complex)

    for index in range(size):
        bits = list(format(index, f"0{height}b"))
        bits[qubit], bits[qubit2] = bits[qubit2], bits[qubit]
        j = int("".join(bits), 2)
        unitary[j, index] = 1

    return unitary


def _control_swap(height: int, control: int, qubit: int, qubit2: int) -> numpy.ndarray:
    size = 2**height
    unitary = numpy.zeros((size, size), dtype=complex)

    for index in range(size):
        bits = list(format(index, f"0{height}b"))

        if bits[control] == "1":
            bits[qubit], bits[qubit2] = bits[qubit2], bits[qubit]

        j = int("".join(bits), 2)
        unitary[j, index] = 1

    return unitary
