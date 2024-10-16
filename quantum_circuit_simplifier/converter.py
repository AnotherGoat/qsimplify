from typing import Callable
from qiskit import QuantumCircuit
from typing_extensions import NamedTuple

from quantum_circuit_simplifier.model import GridNode, QuantumGrid, QuantumGraph, GraphNode, Position
from quantum_circuit_simplifier.utils import get_qubit_indexes, setup_logger

class PlacingData(NamedTuple):
    gate_name: str
    qubits: list[int]
    column: int

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

            target_column = max(columns)
            self.logger.debug("Column %s set as target", target_column)

            target_is_occupied = any(grid.is_occupied(qubit, target_column) for qubit in qubits)

            if target_is_occupied:
                target_column += 1
                self.logger.debug("Rightmost slot is occupied, increasing target column by 1 %s", target_column)

                for qubit in qubits:
                    last_columns[qubit] = target_column

                self.logger.debug("Last columns updated to %s", last_columns)

            self._add_instruction_to_grid(grid, PlacingData(gate_name, qubits, target_column))

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

    def _place_single_qubit_gate(self, grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, column = data
        qubit = qubits[0]

        self.logger.debug("Placing single-qubit gate on qubit %s on column %s", qubit, column)
        grid[qubit, column] = GridNode(gate_name)

    def _place_swap_gate(self, grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, column = data
        first_qubit = qubits[0]
        second_qubit = qubits[1]

        self.logger.debug("Placing swap gate on qubits %s and %s on column %s", first_qubit, second_qubit, column)
        grid[first_qubit, column] = GridNode(gate_name, targets=[second_qubit])
        grid[second_qubit, column] = GridNode(gate_name, targets=[first_qubit])

    def _place_cswap_gate(self, grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, column = data
        control_qubit = qubits[0]
        first_qubit = qubits[1]
        second_qubit = qubits[2]

        self.logger.debug("Placing cswap gate on qubits %s (control), %s and %s on column %s", control_qubit, first_qubit, second_qubit, column)
        grid[control_qubit, column] = GridNode(gate_name, targets=[first_qubit, second_qubit])
        grid[first_qubit, column] = GridNode(gate_name, controlled_by=[control_qubit])
        grid[second_qubit, column] = GridNode(gate_name, controlled_by=[control_qubit])


    def _place_controlled_gate(self, grid: QuantumGrid, data: PlacingData):
        gate_name, qubits, column = data
        target_qubit = qubits.pop()
        control_qubits = qubits

        self.logger.debug("Placing controlled gate on qubits %s (control), and %s (target) on column %s", control_qubits, target_qubit, column)
        grid[target_qubit, column] = GridNode(gate_name, controlled_by=control_qubits)

        for control_qubit in control_qubits:
            grid[control_qubit, column] = GridNode(gate_name, targets=[target_qubit])

    def grid_to_graph(self, grid: QuantumGrid) -> QuantumGraph:
        graph = QuantumGraph()
        self._add_gate_nodes(grid, graph)
        self._add_positional_edges(grid, graph)
        self._add_connection_edges(grid, graph)
        return graph

    @staticmethod
    def _add_gate_nodes(grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                grid_node = grid[row_index, column_index]
                node_position = (row_index, column_index)
                graph.add_gate_node(node_position, GraphNode(grid_node.name, node_position))

    def _add_positional_edges(self, grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                node_position = (row_index, column_index)
                adjacent_positions = self._find_adjacent_positions(column_index, row_index)

                for direction, (adjacent_row, adjacent_column) in adjacent_positions.items():
                    if grid.has_node_at(adjacent_row, adjacent_column):
                        adjacent_position = (adjacent_row, adjacent_column)
                        graph.add_edge(direction, node_position, adjacent_position)

    @staticmethod
    def _find_adjacent_positions(column_index, row_index) -> dict[str, Position]:
        return {
            "up": (row_index - 1, column_index),
            "down": (row_index + 1, column_index),
            "left": (row_index, column_index - 1),
            "right": (row_index, column_index + 1)
        }

    @staticmethod
    def _add_connection_edges(grid: QuantumGrid, graph: QuantumGraph):
        for row_index in range(grid.height):
            for column_index in range(grid.width):
                grid_node = grid[row_index, column_index]

                if len(grid_node.targets) == 0 and len(grid_node.controlled_by) == 0:
                    continue

                node_position = (row_index, column_index)

                for target in grid_node.targets:
                    target_position = (target, column_index)
                    graph.add_edge("targets", node_position, target_position)

                for controller in grid_node.controlled_by:
                    controller_position = (controller, column_index)
                    graph.add_edge("controlled_by", node_position, controller_position)


    def circuit_to_graph(self, circuit: QuantumCircuit) -> QuantumGraph:
        grid = self.circuit_to_grid(circuit)
        return self.grid_to_graph(grid)


    def graph_to_circuit(self, graph: QuantumGraph) -> QuantumCircuit:
        self.logger.debug("Converting graph to circuit")
        circuit = QuantumCircuit(graph.height)
        explored: set[Position] = set()

        for column_index in range(graph.width):
            for row_index in range(graph.height):
                position = (row_index, column_index)

                if position in explored:
                    continue

                explored.add(position)
                graph_node = graph[row_index, column_index]

                if graph_node is None or graph_node.name == "id":
                    continue

                match graph_node.name:
                    case "h":
                        circuit.h(row_index)
                    case "x":
                        circuit.x(row_index)
                    case "y":
                        circuit.y(row_index)
                    case "z":
                        circuit.z(row_index)
                    case "swap":
                        explored.add(self._apply_swap_gate(graph, circuit, position))
                    case "ch":
                        for explored_position in self._apply_controlled_gate(graph, position, circuit.ch):
                            explored.add(explored_position)
                    case "cx":
                        for explored_position in self._apply_controlled_gate(graph, position, circuit.cx):
                            explored.add(explored_position)
                    case "cz":
                        for explored_position in self._apply_controlled_gate(graph, position, circuit.cz):
                            explored.add(explored_position)

        return circuit

    @staticmethod
    def _apply_swap_gate(graph: QuantumGraph, circuit: QuantumCircuit, start: Position) -> Position:
        edges = graph.find_edges(start[0], start[1])
        other_position = edges.targets[0].position

        circuit.swap(start[0], other_position[0])
        return other_position

    @staticmethod
    def _apply_controlled_gate(graph: QuantumGraph, start: Position, method: Callable) -> list[Position]:
        edges = graph.find_edges(start[0], start[1])
        is_controlled = edges.targets == []

        if is_controlled:
            controlled_by_position = edges.controlled_by[0].position
            target_position = start
        else:
            controlled_by_position = start
            target_position = edges.targets[0].position

        method(controlled_by_position[0], target_position[0])
        return [controlled_by_position, target_position]
