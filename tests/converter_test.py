from qiskit import QuantumCircuit

from quantum_circuit_simplifier.converter import circuit_to_graph, GateNode, fill_grid, trim_right_side, \
    circuit_to_grid, GridNode, draw_grid


def test_fill_grid():
    grid = fill_grid("a", 4, 3)

    for row in grid:
        for value in row:
            assert value == "a"

    assert len(grid) == 3
    assert len(grid[0]) == 4


def test_trim_right_side():
    grid = [
        [1, 2, 3, None],
        [4, 5, 6, None],
        [7, 8, 9, None],
    ]

    trimmed_grid = trim_right_side(grid, None)

    assert trimmed_grid == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]


def test_empty_circuit_to_grid():
    circuit = QuantumCircuit(2)
    grid = circuit_to_grid(circuit)

    assert len(grid) == 2
    assert len(grid[0]) == 0
    assert len(grid[1]) == 0


def test_one_qubit_to_grid():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    grid = circuit_to_grid(circuit)

    assert grid[0][0] == GridNode("h")
    assert grid[0][1] == GridNode("x")
    assert grid[0][2] == GridNode("y")
    assert grid[0][3] == GridNode("z")
    assert grid[0][4] == GridNode("x")
    assert grid[0][5] == GridNode("z")
    assert grid[0][6] == GridNode("h")
    assert grid[0][7] == GridNode("y")


def test_two_qubits_to_grid():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.cx(0, 1)
    circuit.ch(1, 0)
    circuit.h(0)
    circuit.y(1)

    grid = circuit_to_grid(circuit)

    assert grid[0][0] == GridNode("h")
    assert grid[1][0] == GridNode("x")

    assert grid[0][1] == GridNode("cx", target=1)
    assert grid[1][1] == GridNode("cx", controlled_by=[0])

    assert grid[0][2] == GridNode("ch", controlled_by=[1])
    assert grid[1][2] == GridNode("ch", target=0)

    assert grid[0][3] == GridNode("h")
    assert grid[1][3] == GridNode("y")


def test_entanglement_to_grid():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    grid = circuit_to_grid(circuit)

    assert grid[0][0] == GridNode("h")
    assert grid[1][0] == GridNode("i")

    assert grid[0][1] == GridNode("cx", target=1)
    assert grid[1][1] == GridNode("cx", controlled_by=[0])


def test_three_qubits_to_grid():
    circuit = QuantumCircuit(3)

    circuit.cx(0, 1)
    circuit.cz(2, 1)
    circuit.h(0)
    circuit.ccx(0, 1, 2)
    circuit.h(2)

    grid = circuit_to_grid(circuit)

    assert grid[0][0] == GridNode("cx", target=1)
    assert grid[1][0] == GridNode("cx", controlled_by=[0])
    assert grid[2][0] == GridNode("i")

    assert grid[0][1] == GridNode("h")
    assert grid[1][1] == GridNode("cz", controlled_by=[2])
    assert grid[2][1] == GridNode("cz", target=1)

    assert grid[0][2] == GridNode("ccx", target=2)
    assert grid[1][2] == GridNode("ccx", target=2)
    assert grid[2][2] == GridNode("ccx", controlled_by=[0, 1])

    assert grid[0][3] == GridNode("i")
    assert grid[1][3] == GridNode("i")
    assert grid[2][3] == GridNode("h")


def test_one_qubit_nodes():
    circuit = QuantumCircuit(1)

    circuit.h(0)
    circuit.x(0)
    circuit.y(0)
    circuit.z(0)
    circuit.x(0)
    circuit.z(0)
    circuit.h(0)
    circuit.y(0)

    graph = circuit_to_graph(circuit)
    gates = graph.gates()

    #assert gates[0].name == "h" and gates[0].qubits == [0]
    assert gates[0] == GateNode("h", [0])
    assert gates[1] == GateNode("x", [0])
    assert gates[2] == GateNode("y", [0])
    assert gates[3] == GateNode("z", [0])
    assert gates[4] == GateNode("x", [0])
    assert gates[5] == GateNode("z", [0])
    assert gates[6] == GateNode("h", [0])
    assert gates[7] == GateNode("y", [0])


def test_two_qubits_nodes():
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.x(1)
    circuit.y(0)
    circuit.z(1)
    circuit.x(0)
    circuit.z(1)
    circuit.h(0)
    circuit.y(1)

    graph = circuit_to_graph(circuit)
    gates = graph.gates()

    assert gates[0] == GateNode("h", [0])
    assert gates[1] == GateNode("x", [1])
    assert gates[2] == GateNode("y", [0])
    assert gates[3] == GateNode("z", [1])
    assert gates[4] == GateNode("x", [0])
    assert gates[5] == GateNode("z", [1])
    assert gates[6] == GateNode("h", [0])
    assert gates[7] == GateNode("y", [1])


def test_two_qubit_gates():
    circuit = QuantumCircuit(2)

    circuit.ch(0, 1)
    circuit.cx(0, 1)
    circuit.cy(0, 1)
    circuit.cz(0, 1)
    circuit.cx(1, 0)
    circuit.cz(1, 0)
    circuit.ch(1, 0)
    circuit.cy(1, 0)

    graph = circuit_to_graph(circuit)
    gates = graph.gates()

    assert gates[0] == GateNode("ch", [0, 1])
    assert gates[1] == GateNode("cx", [0, 1])
    assert gates[2] == GateNode("cy", [0, 1])
    assert gates[3] == GateNode("cz", [0, 1])
    assert gates[4] == GateNode("cx", [1, 0])
    assert gates[5] == GateNode("cz", [1, 0])
    assert gates[6] == GateNode("ch", [1, 0])
    assert gates[7] == GateNode("cy", [1, 0])


def test_one_qubit_horizontal():
    circuit = QuantumCircuit(1)

    circuit.x(0)
    circuit.y(0)
    circuit.z(0)

    graph = circuit_to_graph(circuit)
    gates = graph.gates()

    assert gates[0].left is None
    assert gates[0].right == gates[1]
    assert gates[1].left == gates[0]
    assert gates[1].right == gates[2]
    assert gates[2].left == gates[1]
    assert gates[2].right is None
