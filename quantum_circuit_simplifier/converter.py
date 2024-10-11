from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations
from quantum_circuit_simplifier.model import GridNode, QuantumGrid, QuantumGraph


def circuit_to_grid(circuit: QuantumCircuit) -> QuantumGrid:
    grid = QuantumGrid.create_empty(len(circuit.data), circuit.num_qubits)
    index = 0

    for instruction in circuit.data:
        gate_name = instruction.operation.name
        qubits = get_qubit_indexes(circuit, instruction)

        for qubit in qubits:
            if grid[qubit, index] != GridNode("i"):
                index += 1

        if len(qubits) == 1:
            qubit = qubits[0]
            grid[qubit, index] = GridNode(gate_name)
            continue

        if gate_name == "swap":
            first_qubit = qubits[0]
            second_qubit = qubits[1]

            grid[first_qubit, index] = GridNode(gate_name, targets=[second_qubit])
            grid[second_qubit, index] = GridNode(gate_name, targets=[first_qubit])
            continue

        if gate_name == "cswap":
            control_qubit = qubits[0]
            first_qubit = qubits[1]
            second_qubit = qubits[2]

            grid[control_qubit, index] = GridNode(gate_name, targets=[first_qubit, second_qubit])
            grid[first_qubit, index] = GridNode(gate_name, controlled_by=[control_qubit])
            grid[second_qubit, index] = GridNode(gate_name, controlled_by=[control_qubit])
            continue

        target_qubit = qubits.pop()
        control_qubits = qubits
        grid[target_qubit, index] = GridNode(gate_name, controlled_by=control_qubits)

        for control_qubit in control_qubits:
            grid[control_qubit, index] = GridNode(gate_name, targets=[target_qubit])

    return grid.trim_right_side()


def get_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    qubits = []

    for qubit in instruction.qubits:
        bit_locations: BitLocations = circuit.find_bit(qubit)
        (_, qubit_index) = bit_locations.registers[0]
        qubits.append(qubit_index)

    return qubits


def calculate_gate_index(columns: int, row_index: int, column_index: int) -> int:
    return columns * row_index + column_index


def add_gate_nodes(grid: QuantumGrid, graph: QuantumGraph):
    for row_index in range(grid.height):
        for column_index in range(grid.width):
            grid_node = grid[row_index, column_index]
            node_index = calculate_gate_index(grid.height, row_index, column_index)
            graph.add_node(node_index, name=grid_node.name, position=(row_index, column_index), draw_position=(column_index, grid.height - row_index - 1))


def find_adjacent_positions(column_index, row_index) -> dict[str, tuple[int, int]]:
    return {
        "up": (row_index - 1, column_index),
        "down": (row_index + 1, column_index),
        "left": (row_index, column_index - 1),
        "right": (row_index, column_index + 1)
    }


def add_positional_edges(grid: QuantumGrid, graph: QuantumGraph):
    for row_index in range(grid.height):
        for column_index in range(grid.width):
            node_index = calculate_gate_index(grid.height, row_index, column_index)
            adjacent_positions = find_adjacent_positions(column_index, row_index)

            for direction, (adjacent_row, adjacent_column) in adjacent_positions.items():
                if grid.has_node_at(adjacent_row, adjacent_column):
                    adjacent_index = calculate_gate_index(grid.height, adjacent_row, adjacent_column)
                    graph.add_edge(node_index, adjacent_index, name=direction)


def add_connection_edges(grid: QuantumGrid, graph: QuantumGraph):
    for row_index in range(grid.height):
        for column_index in range(grid.width):
            grid_node = grid[row_index, column_index]

            if len(grid_node.targets) == 0 and len(grid_node.controlled_by) == 0:
                continue

            node_index = calculate_gate_index(grid.height, row_index, column_index)

            for target in grid_node.targets:
                target_index = calculate_gate_index(grid.height, target, column_index)
                graph.add_edge(node_index, target_index, name="target")

            for controller in grid_node.controlled_by:
                controller_index = calculate_gate_index(grid.height, controller, column_index)
                graph.add_edge(node_index, controller_index, name="controlled_by")


def circuit_to_graph(circuit: QuantumCircuit) -> QuantumGraph:
    grid = circuit_to_grid(circuit)
    graph = QuantumGraph()
    add_gate_nodes(grid, graph)
    add_positional_edges(grid, graph)
    add_connection_edges(grid, graph)
    return graph


def graph_to_circuit(graph: QuantumGraph) -> QuantumCircuit:
    pass
