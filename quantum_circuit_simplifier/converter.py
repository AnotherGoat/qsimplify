from networkx.classes import MultiDiGraph
from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations

class GridNode:
    def __init__(self, name: str, targets = None, controlled_by = None):
        self.name = name
        self.targets = [] if targets is None else targets
        self.controlled_by = [] if controlled_by is None else controlled_by


    def __eq__(self, other) -> bool:
        if not isinstance(other, GridNode):
            return NotImplemented

        return self.name == other.name and self.targets == other.targets and self.controlled_by == other.controlled_by


    def __str__(self) -> str:
        name_data = f"name={self.name}"
        target_data = f"targets={self.targets}" if self.targets else ""
        controlled_by_data = f"controlled_by={self.controlled_by}" if self.controlled_by else ""
        non_empty_data = [data for data in [name_data, target_data, controlled_by_data] if data]
        return f"GridNode({', '.join(non_empty_data)})"


def draw_grid(grid: list[list[GridNode]]) -> str:
    rows = []

    for row_index, row in enumerate(grid):
        row_data = "\t".join(str(value) for value in row)
        rows.append(f"{row_index}: {row_data}")

    return "\n".join(rows)


def fill_grid(filler: any, width: int, height: int) -> list[list[any]]:
    return [[filler for _ in range(width)] for _ in range(height)]


def trim_right_side(grid: list[list[any]], filler: any) -> list[list[any]]:
    width = len(grid[0])
    columns_to_trim = 0

    for column in range(width - 1, -1, -1):
        if all(row[column] == filler for row in grid):
            columns_to_trim += 1
        else:
            break

    return [row[0:width - columns_to_trim] for row in grid]


def circuit_to_grid(circuit: QuantumCircuit) -> list[list[GridNode]]:
    grid = fill_grid(GridNode("i"), len(circuit.data), circuit.num_qubits)
    index = 0

    for instruction in circuit.data:
        gate_name = instruction.operation.name
        qubits = get_qubit_indexes(circuit, instruction)

        for qubit in qubits:
            if grid[qubit][index] != GridNode("i"):
                index += 1

        if len(qubits) == 1:
            qubit = qubits[0]
            grid[qubit][index] = GridNode(gate_name)
            continue

        if gate_name == "swap":
            first_qubit = qubits[0]
            second_qubit = qubits[1]

            grid[first_qubit][index] = GridNode(gate_name, targets=[second_qubit])
            grid[second_qubit][index] = GridNode(gate_name, targets=[first_qubit])
            continue

        if gate_name == "cswap":
            control_qubit = qubits[0]
            first_qubit = qubits[1]
            second_qubit = qubits[2]

            grid[control_qubit][index] = GridNode(gate_name, targets=[first_qubit, second_qubit])
            grid[first_qubit][index] = GridNode(gate_name, controlled_by=[control_qubit])
            grid[second_qubit][index] = GridNode(gate_name, controlled_by=[control_qubit])
            continue

        target_qubit = qubits.pop()
        control_qubits = qubits
        grid[target_qubit][index] = GridNode(gate_name, controlled_by=control_qubits)

        for control_qubit in control_qubits:
            grid[control_qubit][index] = GridNode(gate_name, targets=[target_qubit])

    return trim_right_side(grid, GridNode("i"))


def get_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    qubits = []

    for qubit in instruction.qubits:
        bit_locations: BitLocations = circuit.find_bit(qubit)
        (_, qubit_index) = bit_locations.registers[0]
        qubits.append(qubit_index)

    return qubits


def calculate_gate_index(columns: int, row_index: int, column_index: int) -> int:
    return columns * row_index + column_index


def add_gate_nodes(grid: list[list[GridNode]], graph: MultiDiGraph):
    rows = len(grid)
    columns = len(grid[0])

    for row_index in range(rows):
        for column_index in range(columns):
            grid_node = grid[row_index][column_index]
            node_index = calculate_gate_index(columns, row_index, column_index)
            graph.add_node(node_index, name=grid_node.name, position=(row_index, column_index), draw_position=(column_index, rows - row_index - 1))


def find_adjacent_positions(column_index, row_index) -> dict[str, tuple[int, int]]:
    return {
        "up": (row_index - 1, column_index),
        "down": (row_index + 1, column_index),
        "left": (row_index, column_index - 1),
        "right": (row_index, column_index + 1)
    }


def add_edges(grid: list[list[GridNode]], graph: MultiDiGraph):
    rows = len(grid)
    columns = len(grid[0])

    for row_index in range(rows):
        for column_index in range(columns):
            node_index = calculate_gate_index(columns, row_index, column_index)
            adjacent_positions = find_adjacent_positions(column_index, row_index)

            for direction, (adjacent_row, adjacent_column) in adjacent_positions.items():
                if 0 <= adjacent_row < rows and 0 <= adjacent_column < columns:
                    adjacent_index = calculate_gate_index(columns, adjacent_row, adjacent_column)
                    graph.add_edge(node_index, adjacent_index, name=direction)


def circuit_to_graph(circuit: QuantumCircuit) -> MultiDiGraph:
    grid = circuit_to_grid(circuit)
    graph = MultiDiGraph()
    add_gate_nodes(grid, graph)
    add_edges(grid, graph)
    return graph


def graph_to_circuit(graph: MultiDiGraph) -> QuantumCircuit:
    pass
