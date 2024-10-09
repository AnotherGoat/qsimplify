from networkx.classes import DiGraph
from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations


class GridNode:
    def __init__(self, name: str, target = None, controlled_by = None):
        self.name = name
        self.target = target
        self.controlled_by = [] if controlled_by is None else controlled_by


    def __eq__(self, other) -> bool:
        if not isinstance(other, GridNode):
            return NotImplemented

        return self.name == other.name and self.target == other.target and self.controlled_by == other.controlled_by


    def __str__(self) -> str:
        name_data = f"name={self.name}"
        target_data = f"target={self.target}" if self.target else ""
        controlled_by_data = f"controlled_by={self.controlled_by}" if self.controlled_by else ""
        non_empty_data = [data for data in [name_data, target_data, controlled_by_data] if data]
        return f"GridNode({', '.join(non_empty_data)})"


def draw_grid(grid: list[list[GridNode]]) -> str:
    rows = []

    for row_index, row in enumerate(grid):
        row_data = f"{row_index}: {' '.join(str(value) for value in row)}"
        rows.append(row_data)

    return "\n".join(rows)


class GateNode:
    def __init__(self, name: str, qubits: list[int]):
        self.name = name
        self.qubits = qubits
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.target = None
        self.controlled_by = []


    def __eq__(self, other) -> bool:
        if not isinstance(other, GateNode):
            return NotImplemented

        return self.name == other.name and self.qubits == other.qubits


    def __str__(self) -> str:
        left_name = self.left.name if self.left else "None"
        right_name = self.right.name if self.right else "None"
        return f"GateNode(name={self.name}, qubits={self.qubits}, left={left_name}, right={right_name})"


class CircuitGraph(DiGraph):
    def gates(self) -> list[GateNode]:
        return [data["gate"] for (_, data) in self.nodes(data=True)]


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


def circuit_to_grid(circuit: QuantumCircuit):
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

        target_qubit = qubits.pop()
        control_qubits = qubits
        grid[target_qubit][index] = GridNode(gate_name, controlled_by=control_qubits)

        for control_qubit in control_qubits:
            grid[control_qubit][index] = GridNode(gate_name, target=target_qubit)

    return trim_right_side(grid, GridNode("i"))


def get_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
    qubits = []

    for qubit in instruction.qubits:
        bit_locations: BitLocations = circuit.find_bit(qubit)
        (_, qubit_index) = bit_locations.registers[0]
        qubits.append(qubit_index)

    return qubits


def add_gate_nodes(circuit: QuantumCircuit, graph: CircuitGraph):
    for index, instruction in enumerate(circuit.data):
        gate_name = instruction.operation.name
        qubits = get_qubit_indexes(circuit, instruction)
        new_node = GateNode(gate_name, qubits)
        graph.add_node(index, gate=new_node)

        #graph.add_edge()



def circuit_to_graph(circuit: QuantumCircuit) -> CircuitGraph:
    graph = CircuitGraph()
    last_gate_on_qubit = {}

    add_gate_nodes(circuit, graph)

    for index, instruction in enumerate(circuit.data):
        operation = instruction.operation
        qubits = []

        for qubit in instruction.qubits:
            bit_locations: BitLocations = circuit.find_bit(qubit)
            (_, qubit_index) = bit_locations.registers[0]
            qubits.append(qubit_index)

        new_node = GateNode(operation.name, qubits)
        graph.add_node(index, gate=new_node)

        for qubit in qubits:
            if qubit in last_gate_on_qubit:
                last_node = last_gate_on_qubit[qubit]



                new_node.left = last_node
                last_node.right = new_node

            last_gate_on_qubit[qubit] = new_node


    return graph


def graph_to_circuit(graph: CircuitGraph) -> QuantumCircuit:
    pass
