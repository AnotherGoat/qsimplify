from qiskit import QuantumCircuit
from typing_extensions import NamedTuple

from quantum_circuit_simplifier.model import GridNode, QuantumGrid, QuantumGraph
from quantum_circuit_simplifier.utils import get_qubit_indexes, setup_logger

class PlacingData(NamedTuple):
    gate_name: str
    qubits: list[int]
    last_columns: list[int]

class Converter:
    def __init__(self):
        self.logger = setup_logger("Converter")

    def circuit_to_grid(self, circuit: QuantumCircuit) -> QuantumGrid:
        self.logger.debug("Converting circuit to grid\n%s", circuit.draw())
        grid = QuantumGrid.create_empty(len(circuit.data), circuit.num_qubits)
        self.logger.debug("Created empty %sx%s grid", len(circuit.data), circuit.num_qubits)
        last_columns = [0 for _ in range(grid.height)]

        for instruction in circuit.data:
            self.logger.debug("This is what the grid looks like now\n%s", grid)

            self.logger.debug("Processing instruction %s", instruction)
            gate_name = instruction.operation.name
            qubits = get_qubit_indexes(circuit, instruction)
            self.logger.debug("Instruction qubit indexes are %s", qubits)

            columns = [last_columns[qubit] for qubit in qubits]
            self.logger.debug("Last columns for each qubit are %s", columns)

            max_column = max(columns)
            max_qubit = qubits[columns.index(max_column)]
            self.logger.debug("Rightmost qubit %s found at column %s", max_qubit, max_column)

            if grid.is_occupied(max_qubit, max_column):
                self.logger.debug("Rightmost slot is occupied")
                for qubit in qubits:
                    last_columns[qubit] = max_column + 1

                self.logger.debug("Last columns updated to %s", last_columns)

            self._add_instruction_to_grid(grid, PlacingData(gate_name, qubits, last_columns))

        self.logger.debug("This is the grid before trimming its right side\n%s", grid)
        trimmed_grid = grid.trim_right_side()
        self.logger.debug("After trimming, this is the result\n%s", trimmed_grid)
        self.logger.debug("For comparison, this is the original circuit\n%s", circuit.draw())
        return trimmed_grid


    def _add_instruction_to_grid(self, grid, data: PlacingData):
        if len(data.qubits) == 1:
            self._place_single_qubit_gate(grid, data)
        elif data.gate_name == "swap":
            self._place_swap_gate(grid, data)
        elif data.gate_name == "cswap":
            self._place_cswap_gate(grid, data)
        else:
            self._place_controlled_gate(grid, data)

    @staticmethod
    def _place_single_qubit_gate(grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, last_columns = data
        qubit = qubits[0]

        grid[qubit, last_columns[qubit]] = GridNode(gate_name)

    @staticmethod
    def _place_swap_gate(grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, last_columns = data
        first_qubit = qubits[0]
        second_qubit = qubits[1]

        grid[first_qubit, last_columns[first_qubit]] = GridNode(gate_name, targets=[second_qubit])
        grid[second_qubit, last_columns[second_qubit]] = GridNode(gate_name, targets=[first_qubit])

    @staticmethod
    def _place_cswap_gate(grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, last_columns = data
        control_qubit = qubits[0]
        first_qubit = qubits[1]
        second_qubit = qubits[2]

        grid[control_qubit, last_columns[control_qubit]] = GridNode(gate_name, targets=[first_qubit, second_qubit])
        grid[first_qubit, last_columns[first_qubit]] = GridNode(gate_name, controlled_by=[control_qubit])
        grid[second_qubit, last_columns[second_qubit]] = GridNode(gate_name, controlled_by=[control_qubit])


    @staticmethod
    def _place_controlled_gate(grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, last_columns = data
        target_qubit = qubits.pop()
        control_qubits = qubits
        grid[target_qubit, last_columns[target_qubit]] = GridNode(gate_name, controlled_by=control_qubits)

        for control_qubit in control_qubits:
            grid[control_qubit, last_columns[control_qubit]] = GridNode(gate_name, targets=[target_qubit])

    @staticmethod
    def _calculate_gate_index(columns: int, row_index: int, column_index: int) -> int:
        return columns * row_index + column_index


    def _add_gate_nodes(self, grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                grid_node = grid[row_index, column_index]
                node_index = self._calculate_gate_index(grid.width, row_index, column_index)
                graph.add_node(node_index, name=grid_node.name, position=(row_index, column_index), draw_position=(column_index, grid.height - row_index - 1))


    def _find_adjacent_positions(self, column_index, row_index) -> dict[str, tuple[int, int]]:
        return {
            "up": (row_index - 1, column_index),
            "down": (row_index + 1, column_index),
            "left": (row_index, column_index - 1),
            "right": (row_index, column_index + 1)
        }


    def _add_positional_edges(self, grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                node_index = self._calculate_gate_index(grid.width, row_index, column_index)
                adjacent_positions = self._find_adjacent_positions(column_index, row_index)

                for direction, (adjacent_row, adjacent_column) in adjacent_positions.items():
                    if grid.has_node_at(adjacent_row, adjacent_column):
                        adjacent_index = self._calculate_gate_index(grid.width, adjacent_row, adjacent_column)
                        graph.add_edge(node_index, adjacent_index, name=direction)


    def _add_connection_edges(self, grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                grid_node = grid[row_index, column_index]

                if len(grid_node.targets) == 0 and len(grid_node.controlled_by) == 0:
                    continue

                node_index = self._calculate_gate_index(grid.width, row_index, column_index)

                for target in grid_node.targets:
                    target_index = self._calculate_gate_index(grid.width, target, column_index)
                    graph.add_edge(node_index, target_index, name="target")

                for controller in grid_node.controlled_by:
                    controller_index = self._calculate_gate_index(grid.width, controller, column_index)
                    graph.add_edge(node_index, controller_index, name="controlled_by")


    def circuit_to_graph(self, circuit: QuantumCircuit) -> QuantumGraph:
        grid = self.circuit_to_grid(circuit)
        graph = QuantumGraph()
        self._add_gate_nodes(grid, graph)
        self._add_positional_edges(grid, graph)
        self._add_connection_edges(grid, graph)
        return graph


    def graph_to_circuit(self, graph: QuantumGraph) -> QuantumCircuit:
        pass
