from typing import Callable
from qiskit import QuantumCircuit
from typing_extensions import NamedTuple

from qsimplify.model import QuantumGraph, Position, GateName, GraphNode, GraphBuilder, CircuitBuilder
from qsimplify.utils import find_qubit_indexes, setup_logger, find_bit_indexes

class GraphPlacingData(NamedTuple):
    builder: GraphBuilder
    gate_name: GateName
    qubits: list[int]
    bits: list[int]
    params: list
    column: int

class CircuitPlacingData(NamedTuple):
    builder: CircuitBuilder
    graph: QuantumGraph
    graph_node: GraphNode
    explored: set[Position]
    start: Position

class Converter:
    def __init__(self):
        self.logger = setup_logger("Converter")
        self._circuit_to_graph_handlers: dict[GateName, Callable[[GraphPlacingData], None]] = {
            GateName.H: self._add_single_gate_to_graph,
            GateName.X: self._add_single_gate_to_graph,
            GateName.Y: self._add_single_gate_to_graph,
            GateName.Z: self._add_single_gate_to_graph,
            GateName.RX: self._add_rotation_gate_to_graph,
            GateName.RY: self._add_rotation_gate_to_graph,
            GateName.RZ: self._add_rotation_gate_to_graph,
            GateName.MEASURE: self._add_measure_gate_to_graph,
            GateName.SWAP: self._add_swap_gate_to_graph,
            GateName.CH: self._add_controlled_gate_to_graph,
            GateName.CX: self._add_controlled_gate_to_graph,
            GateName.CZ: self._add_cz_gate_to_graph,
            GateName.CSWAP: self._add_cswap_gate_to_graph,
            GateName.CCX: self._add_ccx_gate_to_graph,
        }
        self._graph_to_circuit_handlers: dict[GateName, Callable[[CircuitPlacingData], None]] = {
            GateName.H: self._add_single_gate_to_circuit,
            GateName.X: self._add_single_gate_to_circuit,
            GateName.Y: self._add_single_gate_to_circuit,
            GateName.Z: self._add_single_gate_to_circuit,
            GateName.RX: self._add_rotation_gate_to_circuit,
            GateName.RY: self._add_rotation_gate_to_circuit,
            GateName.RZ: self._add_rotation_gate_to_circuit,
            GateName.MEASURE: self._add_measure_gate_to_circuit,
            GateName.SWAP: self._add_swap_gate_to_circuit,
            GateName.CH: self._add_controlled_gate_to_circuit,
            GateName.CX: self._add_controlled_gate_to_circuit,
            GateName.CZ: self._add_cz_gate_to_circuit,
            GateName.CSWAP: self._add_cswap_gate_to_circuit,
            GateName.CCX: self._add_ccx_gate_to_circuit,
        }

    def circuit_to_graph(self, circuit: QuantumCircuit) -> QuantumGraph:
        self.logger.debug("Converting circuit to graph\n%s", circuit.draw())
        builder = GraphBuilder()

        last_columns = [0 for _ in range(circuit.num_qubits)]

        for instruction in circuit.data:
            self.logger.debug("This is what the graph looks like now\n%s", builder)

            self.logger.debug("Processing instruction %s", instruction)
            gate_name = GateName.from_str(instruction.operation.name)

            if gate_name in (GateName.ID, GateName.BARRIER):
                self.logger.debug("Skipping empty instruction")
                continue

            qubits = find_qubit_indexes(circuit, instruction)
            self.logger.debug("Instruction qubit indexes are %s", qubits)

            columns = [last_columns[qubit] for qubit in qubits]
            self.logger.debug("Last columns for each qubit are %s", columns)

            target_column = max(columns)
            self.logger.debug("Column %s set as target", target_column)

            target_is_occupied = any(builder.is_occupied(qubit, target_column) for qubit in qubits)

            if target_is_occupied:
                target_column += 1
                self.logger.debug("Rightmost slot is occupied, increasing target column by 1 %s", target_column)

                for qubit in qubits:
                    last_columns[qubit] = target_column

                self.logger.debug("Last columns updated to %s", last_columns)

            bits = find_bit_indexes(circuit, instruction)
            params = instruction.operation.params
            placing_data = GraphPlacingData(builder, gate_name, qubits, bits, params, target_column)
            self._add_instruction_to_graph(placing_data)

        graph = builder.build()
        self.logger.debug("After building the graph, this is the result\n%s", graph)
        self.logger.debug("For comparison, this is the original circuit\n%s", circuit.draw())
        return graph

    def _add_instruction_to_graph(self, data: GraphPlacingData):
        self._circuit_to_graph_handlers[data.gate_name](data)

    def _add_single_gate_to_graph(self, data: GraphPlacingData):
        builder, gate_name, qubits, _, _, column = data
        self.logger.debug("Placing single-qubit gate on qubit %s on column %s", qubits[0], column)
        builder.add_single(gate_name, qubits[0], column)

    def _add_rotation_gate_to_graph(self, data: GraphPlacingData):
        builder, gate_name, qubits, _, params, column = data
        self.logger.debug("Placing rotation gate with angle %s on qubit %s on column %s", params[0], qubits[0], column)
        builder.add_rotation(gate_name, params[0], qubits[0], column)

    def _add_measure_gate_to_graph(self, data: GraphPlacingData):
        builder, _, qubits, bits, _, column = data
        self.logger.debug("Placing measure gate on qubit %s to bit %s on column %s", qubits[0], bits[0], column)
        builder.add_measure(qubits[0], bits[0], column)

    def _add_swap_gate_to_graph(self, data: GraphPlacingData):
        builder, _, qubits, _, _, column = data
        self.logger.debug("Placing swap gate on qubits %s and %s on column %s", qubits[0], qubits[1], column)
        builder.add_swap(qubits[0], qubits[1], column)

    def _add_cz_gate_to_graph(self, data: GraphPlacingData):
        builder, _, qubits, _, _, column = data
        self.logger.debug("Placing cz gate on qubits %s and %s on column %s", qubits[0], qubits[1], column)
        builder.add_cz(qubits[0], qubits[1], column)

    def _add_cswap_gate_to_graph(self, data: GraphPlacingData):
        builder, _, qubits, _, _, column = data
        self.logger.debug("Placing cswap gate on qubits %s (control), %s (target) and %s (target) on column %s", qubits[0], qubits[1], qubits[2], column)
        builder.add_cswap(qubits[0], qubits[1], qubits[2], column)

    def _add_controlled_gate_to_graph(self, data: GraphPlacingData):
        builder, gate_name, qubits, _, _, column = data
        self.logger.debug("Placing controlled gate on qubits %s (control) and %s (target) on column %s", qubits[0], qubits[1], column)
        builder.add_control(gate_name, qubits[0], qubits[1], column)

    def _add_ccx_gate_to_graph(self, data: GraphPlacingData):
        builder, _, qubits, _, _, column = data
        self.logger.debug("Placing ccx gate on qubits %s (control), %s (control) and %s (target) on column %s", qubits[0], qubits[1], qubits[2], column)
        builder.add_ccx(qubits[0], qubits[1], qubits[2], column)

    def graph_to_circuit(self, graph: QuantumGraph, add_build_steps: bool = False, circuit_name: str = "circuit") -> QuantumCircuit | tuple[QuantumCircuit, str]:
        self.logger.debug("Converting graph to circuit")
        builder = CircuitBuilder(graph.height, name=circuit_name)
        explored: set[Position] = set()

        for column_index in range(graph.width):
            for row_index in range(graph.height):
                position = (row_index, column_index)
                self._add_to_circuit(builder, graph, explored, position)

        return builder.build(add_build_steps)

    def _add_to_circuit(self, builder: CircuitBuilder, graph: QuantumGraph, explored: set[Position], position: Position):
        if position in explored:
            return

        explored.add(position)
        graph_node = graph[*position]

        if graph_node is None or graph_node.name in (GateName.ID, GateName.BARRIER):
            return

        placing_data = CircuitPlacingData(builder, graph, graph_node, explored, position)
        self._add_instruction_to_circuit(placing_data)

    def _add_instruction_to_circuit(self, data: CircuitPlacingData):
        self._graph_to_circuit_handlers[data.graph_node.name](data)

    @staticmethod
    def _add_single_gate_to_circuit(data: CircuitPlacingData):
        builder, _, graph_node, _, start = data
        builder.add_single(graph_node.name, start[0])

    @staticmethod
    def _add_rotation_gate_to_circuit(data: CircuitPlacingData):
        builder, _, graph_node, _, start = data
        builder.add_rotation(graph_node.name, graph_node.rotation, start[0])

    @staticmethod
    def _add_measure_gate_to_circuit(data: CircuitPlacingData):
        builder, _, graph_node, _, start = data
        builder.add_measure(start[0], graph_node.measure_to)

    @staticmethod
    def _add_swap_gate_to_circuit(data: CircuitPlacingData):
        builder, graph, _, explored, start = data
        edges = graph.node_edge_data(*start)
        other_position = edges.swaps_with.position
        builder.add_swap(start[0], other_position[0])
        explored.add(other_position)

    @staticmethod
    def _add_controlled_gate_to_circuit(data: CircuitPlacingData):
        builder, graph, graph_node, explored, start = data
        edges = graph.node_edge_data(*start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            target_position = start
        else:
            controller_position = start
            target_position = edges.targets[0].position

        builder.add_control(graph_node.name, controller_position[0], target_position[0])
        explored.add(controller_position)
        explored.add(target_position)

    @staticmethod
    def _add_cz_gate_to_circuit(data: CircuitPlacingData):
        builder, graph, _, explored, start = data
        edges = graph.node_edge_data(*start)
        other_position = edges.works_with[0].position
        builder.add_cz(start[0], other_position[0])
        explored.add(other_position)

    @staticmethod
    def _add_cswap_gate_to_circuit(data: CircuitPlacingData):
        builder, graph, _, explored, start = data
        edges = graph.node_edge_data(*start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            first_position = start
            second_position = edges.swaps_with.position
        else:
            controller_position = start
            first_position = edges.targets[0].position
            second_position = edges.targets[1].position

        builder.add_cswap(controller_position[0], first_position[0], second_position[0])
        explored.add(controller_position)
        explored.add(first_position)
        explored.add(second_position)

    @staticmethod
    def _add_ccx_gate_to_circuit(data: CircuitPlacingData):
        builder, graph, _, explored, start = data

        edges = graph.node_edge_data(*start)
        is_target = edges.targets == []

        if is_target:
            first_controller_position = edges.controlled_by[0].position
            second_controller_position = edges.controlled_by[1].position
            target_position = start
        else:
            first_controller_position = start
            second_controller_position = edges.works_with[0].position
            target_position = edges.targets[0].position

        builder.add_ccx(first_controller_position[0], second_controller_position[0], target_position[0])
        explored.add(first_controller_position)
        explored.add(second_controller_position)
        explored.add(target_position)
