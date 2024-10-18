from itertools import product
from typing import Callable
from qiskit import QuantumCircuit
from typing_extensions import NamedTuple

from quantum_circuit_simplifier.model import QuantumGraph, Position, EdgeName, \
    GateName
from quantum_circuit_simplifier.utils import get_qubit_indexes, setup_logger

class GraphPlacingData(NamedTuple):
    gate_name: GateName
    qubits: list[int]
    column: int

class CircuitPlacingData(NamedTuple):
    pass

class Converter:
    def __init__(self):
        self.logger = setup_logger("Converter")

    def circuit_to_graph(self, circuit: QuantumCircuit) -> QuantumGraph:
        self.logger.debug("Converting circuit to graph\n%s", circuit.draw())
        graph = QuantumGraph()

        last_columns = [0 for _ in range(circuit.num_qubits)]

        for instruction in circuit.data:
            self.logger.debug("This is what the graph looks like now\n%s", graph)

            self.logger.debug("Processing instruction %s", instruction)
            gate_name = GateName.from_str(instruction.operation.name)
            qubits = get_qubit_indexes(circuit, instruction)
            self.logger.debug("Instruction qubit indexes are %s", qubits)

            columns = [last_columns[qubit] for qubit in qubits]
            self.logger.debug("Last columns for each qubit are %s", columns)

            target_column = max(columns)
            self.logger.debug("Column %s set as target", target_column)

            target_is_occupied = any(graph.is_occupied(qubit, target_column) for qubit in qubits)

            if target_is_occupied:
                target_column += 1
                self.logger.debug("Rightmost slot is occupied, increasing target column by 1 %s", target_column)

                for qubit in qubits:
                    last_columns[qubit] = target_column

                self.logger.debug("Last columns updated to %s", last_columns)

            self._add_instruction_to_graph(graph, GraphPlacingData(gate_name, qubits, target_column))

        self.logger.debug("This is the graph before filling empty spaces\n%s", graph)
        graph.fill_empty_spaces()
        self.logger.debug("This is the graph before adding positional edges\n%s", graph)
        graph.fill_positional_edges()
        self.logger.debug("After adding all the edges, this is the result\n%s", graph)
        self.logger.debug("For comparison, this is the original circuit\n%s", circuit.draw())
        return graph


    def _add_instruction_to_graph(self, graph: QuantumGraph, data: GraphPlacingData):
        if len(data.qubits) == 1:
            self._add_single_qubit_gate_to_graph(graph, data)
            return

        match data.gate_name:
            case GateName.SWAP:
                self._add_swap_gate_to_graph(graph, data)
            case GateName.CSWAP:
                self._add_cswap_gate_to_graph(graph, data)
            case _:
                self._add_controlled_gate_to_graph(graph, data)

    def _add_single_qubit_gate_to_graph(self, graph: QuantumGraph, data: GraphPlacingData):
        gate_name, qubits, column = data
        qubit = qubits[0]

        self.logger.debug("Placing single-qubit gate on qubit %s on column %s", qubit, column)
        graph.add_new_node(gate_name, (qubit, column))

    def _add_swap_gate_to_graph(self, graph: QuantumGraph, data: GraphPlacingData):
        gate_name, qubits, column = data
        first_position = (qubits[0], column)
        second_position = (qubits[1], column)

        self.logger.debug("Placing swap gate on qubits %s and %s on column %s", qubits[0], qubits[1], column)
        graph.add_new_node(gate_name, first_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, first_position, second_position)

        graph.add_new_node(gate_name, second_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, second_position, first_position)

    def _add_cswap_gate_to_graph(self, graph: QuantumGraph, data: GraphPlacingData):
        gate_name, qubits, column = data
        control_position = (qubits[0], column)
        first_position = (qubits[1], column)
        second_position = (qubits[2], column)

        self.logger.debug("Placing cswap gate on qubits %s (control), %s and %s on column %s", qubits[0], qubits[1], qubits[2], column)
        graph.add_new_node(gate_name, control_position)
        graph.add_new_edge(EdgeName.TARGETS, control_position, first_position)
        graph.add_new_edge(EdgeName.TARGETS, control_position, second_position)

        graph.add_new_node(gate_name, first_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, first_position, second_position)
        graph.add_new_edge(EdgeName.CONTROLLED_BY, first_position, control_position)

        graph.add_new_node(gate_name, second_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, second_position, first_position)
        graph.add_new_edge(EdgeName.CONTROLLED_BY, second_position, control_position)

    def _add_controlled_gate_to_graph(self, graph: QuantumGraph, data: GraphPlacingData):
        gate_name, qubits, column = data
        target_position = (qubits.pop(), column)
        control_positions = [(qubit, column) for qubit in qubits]

        self.logger.debug("Placing controlled gate on qubits %s (control), and %s (target) on column %s", qubits, target_position[0], column)
        graph.add_new_node(gate_name, target_position)

        for control_position in control_positions:
            graph.add_new_node(gate_name, control_position)
            graph.add_new_edge(EdgeName.TARGETS, control_position, target_position)
            graph.add_new_edge(EdgeName.CONTROLLED_BY, target_position, control_position)

            for other_control_position in control_positions:
                if control_position == other_control_position:
                    continue

                graph.add_new_edge(EdgeName.WORKS_WITH, control_position, other_control_position)


    def graph_to_circuit(self, graph: QuantumGraph) -> (QuantumCircuit, list[str]):
        self.logger.debug("Converting graph to circuit")
        circuit = QuantumCircuit(graph.height)
        build_steps = [f"circuit = QuantumCircuit({graph.height})"]
        explored: set[Position] = set()

        for position in product(range(graph.height), range(graph.width)):
            self._add_to_circuit(graph, circuit, build_steps, explored, position)

        return circuit, build_steps

    def _add_to_circuit(self, graph: QuantumGraph, circuit: QuantumCircuit, build_steps: list[str], explored: set[Position], position: Position):
        if position in explored:
            return

        explored.add(position)
        graph_node = graph[*position]

        if graph_node is None or graph_node.name == GateName.ID:
            return

        match graph_node.name:
            case GateName.H:
                circuit.h(position[0])
                build_steps.append(f"circuit.h({position[0]})")
            case GateName.X:
                circuit.x(position[0])
                build_steps.append(f"circuit.x({position[0]})")
            case GateName.Y:
                circuit.y(position[0])
                build_steps.append(f"circuit.y({position[0]})")
            case GateName.Z:
                circuit.z(position[0])
                build_steps.append(f"circuit.z({position[0]})")
            case GateName.SWAP:
                explored.add(self._add_swap_gate_to_circuit(graph, circuit, build_steps, position))
            case GateName.CH:
                for explored_position in self._add_controlled_gate_to_circuit(graph, build_steps, position, circuit.ch):
                    explored.add(explored_position)
            case GateName.CX:
                for explored_position in self._add_controlled_gate_to_circuit(graph, build_steps, position, circuit.cx):
                    explored.add(explored_position)
            case GateName.CZ:
                for explored_position in self._add_controlled_gate_to_circuit(graph, build_steps, position, circuit.cz):
                    explored.add(explored_position)
            case GateName.CCX:
                for explored_position in self._add_controlled_gate_to_circuit(graph, build_steps, position, circuit.ccx):
                    explored.add(explored_position)
            case GateName.CSWAP:
                for explored_position in self._add_cswap_gate_to_circuit(graph, build_steps, circuit, position):
                    explored.add(explored_position)

    @staticmethod
    def _add_swap_gate_to_circuit(graph: QuantumGraph, circuit: QuantumCircuit, build_steps: list[str], start: Position) -> Position:
        edges = graph.find_edges(*start)
        other_position = edges.swaps_with.position

        circuit.swap(start[0], other_position[0])
        build_steps.append(f"circuit.swap({start[0]}, {other_position[0]})")
        return other_position

    @staticmethod
    def _add_controlled_gate_to_circuit(graph: QuantumGraph, build_steps: list[str], start: Position, method: Callable) -> list[Position]:
        edges = graph.find_edges(*start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            target_position = start
        else:
            controller_position = start
            target_position = edges.targets[0].position

        method(controller_position[0], target_position[0])
        build_steps.append(f"circuit.{method.__name__}({controller_position[0]}, {target_position[0]})")
        return [controller_position, target_position]


    @staticmethod
    def _add_cswap_gate_to_circuit(graph: QuantumGraph, build_steps: list[str], circuit: QuantumCircuit, start: Position) -> list[Position]:
        edges = graph.find_edges(*start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            first_position = start
            second_position = edges.swaps_with.position
        else:
            controller_position = start
            first_position = edges.targets[0].position
            second_position = edges.targets[1].position

        circuit.cswap(controller_position[0], first_position[0], second_position[0])
        build_steps.append(f"circuit.cswap({controller_position[0]}, {first_position[0]}, {second_position[0]})")
        return [controller_position, first_position, second_position]


    @staticmethod
    def _add_ccx_gate_to_circuit(graph: QuantumGraph, build_steps: list[str], circuit: QuantumCircuit, start: Position) -> list[Position]:
        edges = graph.find_edges(*start)
        is_target = edges.targets == []

        if is_target:
            first_controller_position = edges.controlled_by[0].position
            second_controller_position = edges.controlled_by[1].position
            target_position = start
        else:
            first_controller_position = start
            second_controller_position = edges.works_with[0].position
            target_position = edges.targets[0].position

        circuit.ccx(first_controller_position[0], second_controller_position[0], target_position[0])
        build_steps.append(f"circuit.ccx({first_controller_position[0]}, {second_controller_position[0]}, {target_position[0]})")
        return [first_controller_position, second_controller_position, target_position]
