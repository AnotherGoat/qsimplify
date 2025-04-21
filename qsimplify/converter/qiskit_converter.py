from typing import Callable

from qiskit import QuantumCircuit
from qiskit.circuit import CircuitInstruction
from qiskit.circuit.quantumcircuit import BitLocations
from typing_extensions import NamedTuple

from qsimplify.converter import GraphConverter
from qsimplify.model import (
    CircuitBuilder,
    GateName,
    GraphBuilder,
    GraphNode,
    Position,
    QuantumGraph,
)
from qsimplify.utils import setup_logger

class GraphPlacingData(NamedTuple):
    builder: GraphBuilder
    gate_name: GateName
    qubits: list[int]
    bits: list[int]
    params: list
    column: int


class CircuitPlacingData(NamedTuple):
    circuit: CircuitBuilder
    graph: QuantumGraph
    graph_node: GraphNode
    explored: set[Position]
    start: Position


# TODO: Make this converter implement the abstract base class properly
class QiskitConverter(GraphConverter[QuantumCircuit]):
    def __init__(self) -> None:
        self._logger = setup_logger("QiskitConverter")
        self._to_graph_handlers: dict[GateName, Callable[[GraphPlacingData], None]] = {
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
        self._from_graph_handlers: dict[GateName, Callable[[CircuitPlacingData], None]] = {
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

    def to_graph(self, data: QuantumCircuit) -> QuantumGraph:
        self._logger.debug("Converting circuit to graph\n%s", data.draw())
        builder = GraphBuilder()

        last_columns = [0 for _ in range(data.num_qubits)]

        for instruction in data.data:
            self._logger.debug("This is what the graph looks like now\n%s", builder)

            self._logger.debug("Processing instruction %s", instruction)
            gate_name = GateName.from_str(instruction.operation.name)

            if gate_name in (GateName.ID, GateName.BARRIER):
                self._logger.debug("Skipping empty instruction")
                continue

            qubits = self._find_qubit_indexes(data, instruction)
            self._logger.debug("Instruction qubit indexes are %s", qubits)

            columns = [last_columns[qubit] for qubit in qubits]
            self._logger.debug("Last columns for each qubit are %s", columns)

            target_column = max(columns)
            self._logger.debug("Column %s set as target", target_column)

            target_is_occupied = any(builder.is_occupied(qubit, target_column) for qubit in qubits)

            if target_is_occupied:
                target_column += 1
                self._logger.debug(
                    "Rightmost slot is occupied, increasing target column by 1 %s",
                    target_column,
                )

                for qubit in qubits:
                    last_columns[qubit] = target_column

                self._logger.debug("Last columns updated to %s", last_columns)

            bits = self._find_bit_indexes(data, instruction)
            params = instruction.operation.params
            context = GraphPlacingData(builder, gate_name, qubits, bits, params, target_column)
            self._add_instruction_to_graph(context)

        graph = builder.build()
        self._logger.debug("After building the graph, this is the result\n%s", graph)
        self._logger.debug("For comparison, this is the original circuit\n%s", data.draw())
        return graph

    @staticmethod
    def _find_qubit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
        qubits = []

        for qubit in instruction.qubits:
            bit_locations: BitLocations = circuit.find_bit(qubit)

            for _, qubit_index in bit_locations.registers:
                qubits.append(qubit_index)

        return qubits

    @staticmethod
    def _find_bit_indexes(circuit: QuantumCircuit, instruction: CircuitInstruction) -> list[int]:
        bits = []

        for bit in instruction.clbits:
            bit_locations: BitLocations = circuit.find_bit(bit)

            for _, bit_index in bit_locations.registers:
                bits.append(bit_index)

        return bits

    def _add_instruction_to_graph(self, data: GraphPlacingData) -> None:
        self._to_graph_handlers[data.gate_name](data)

    def _add_single_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, gate_name, qubits, column = (
            data.builder,
            data.gate_name,
            data.qubits,
            data.column,
        )
        self._logger.debug("Placing single-qubit gate on qubit %s on column %s", qubits[0], column)
        builder.put_single(gate_name, qubits[0], column)

    def _add_rotation_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, gate_name, qubits, params, column = (
            data.builder,
            data.gate_name,
            data.qubits,
            data.params,
            data.column,
        )
        self._logger.debug(
            "Placing rotation gate with angle %s on qubit %s on column %s",
            params[0],
            qubits[0],
            column,
        )
        builder.put_rotation(gate_name, params[0], qubits[0], column)

    def _add_measure_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, qubits, bits, column = (
            data.builder,
            data.qubits,
            data.bits,
            data.column,
        )
        self._logger.debug(
            "Placing measure gate on qubit %s to bit %s on column %s",
            qubits[0],
            bits[0],
            column,
        )
        builder.put_measure(qubits[0], bits[0], column)

    def _add_swap_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, qubits, column = data.builder, data.qubits, data.column
        self._logger.debug(
            "Placing swap gate on qubits %s and %s on column %s",
            qubits[0],
            qubits[1],
            column,
        )
        builder.put_swap(qubits[0], qubits[1], column)

    def _add_cz_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, qubits, column = data.builder, data.qubits, data.column
        self._logger.debug(
            "Placing cz gate on qubits %s and %s on column %s",
            qubits[0],
            qubits[1],
            column,
        )
        builder.put_cz(qubits[0], qubits[1], column)

    def _add_cswap_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, qubits, column = data.builder, data.qubits, data.column
        self._logger.debug(
            "Placing cswap gate on qubits %s (control), %s (target) and %s (target) on column %s",
            qubits[0],
            qubits[1],
            qubits[2],
            column,
        )
        builder.put_cswap(qubits[0], qubits[1], qubits[2], column)

    def _add_controlled_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, gate_name, qubits, column = (
            data.builder,
            data.gate_name,
            data.qubits,
            data.column,
        )
        self._logger.debug(
            "Placing controlled gate on qubits %s (control) and %s (target) on column %s",
            qubits[0],
            qubits[1],
            column,
        )
        builder.put_control(gate_name, qubits[0], qubits[1], column)

    def _add_ccx_gate_to_graph(self, data: GraphPlacingData) -> None:
        builder, qubits, column = data.builder, data.qubits, data.column
        self._logger.debug(
            "Placing ccx gate on qubits %s (control), %s (control) and %s (target) on column %s",
            qubits[0],
            qubits[1],
            qubits[2],
            column,
        )
        builder.put_ccx(qubits[0], qubits[1], qubits[2], column)

    def from_graph(
        self,
        graph: QuantumGraph,
    ) -> QuantumCircuit | tuple[QuantumCircuit, str]:
        self._logger.debug("Converting graph to circuit")
        builder = CircuitBuilder(graph.height)
        explored: set[Position] = set()

        for column_index in range(graph.width):
            for row_index in range(graph.height):
                position = Position(row_index, column_index)
                self._add_to_circuit(builder, graph, explored, position)

        return builder.build()

    def _add_to_circuit(
        self,
        builder: CircuitBuilder,
        graph: QuantumGraph,
        explored: set[Position],
        position: Position,
    ) -> None:
        if position in explored:
            return

        explored.add(position)
        graph_node = graph[position]

        if graph_node is None or graph_node.name in (GateName.ID, GateName.BARRIER):
            return

        placing_data = CircuitPlacingData(builder, graph, graph_node, explored, position)
        self._add_instruction_to_circuit(placing_data)

    def _add_instruction_to_circuit(self, data: CircuitPlacingData) -> None:
        self._from_graph_handlers[data.graph_node.name](data)

    @staticmethod
    def _add_single_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph_node, start = data.circuit, data.graph_node, data.start
        builder.add_single(graph_node.name, start.row)

    @staticmethod
    def _add_rotation_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph_node, start = data.circuit, data.graph_node, data.start
        builder.add_rotation(graph_node.name, graph_node.rotation, start.row)

    @staticmethod
    def _add_measure_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph_node, start = data.circuit, data.graph_node, data.start
        builder.add_measure(start.row, graph_node.measure_to)

    @staticmethod
    def _add_swap_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph, explored, start = (
            data.circuit,
            data.graph,
            data.explored,
            data.start,
        )
        edges = graph.node_edge_data(start)
        other_position = edges.swaps_with.position
        builder.add_swap(start.row, other_position.row)
        explored.add(other_position)

    @staticmethod
    def _add_controlled_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph, graph_node, explored, start = (
            data.circuit,
            data.graph,
            data.graph_node,
            data.explored,
            data.start,
        )
        edges = graph.node_edge_data(start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            target_position = start
        else:
            controller_position = start
            target_position = edges.targets[0].position

        builder.add_control(graph_node.name, controller_position.row, target_position.row)
        explored.add(controller_position)
        explored.add(target_position)

    @staticmethod
    def _add_cz_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph, explored, start = (
            data.circuit,
            data.graph,
            data.explored,
            data.start,
        )
        edges = graph.node_edge_data(start)
        other_position = edges.works_with[0].position
        builder.add_cz(start.row, other_position.row)
        explored.add(other_position)

    @staticmethod
    def _add_cswap_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph, explored, start = (
            data.circuit,
            data.graph,
            data.explored,
            data.start,
        )
        edges = graph.node_edge_data(start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            first_position = start
            second_position = edges.swaps_with.position
        else:
            controller_position = start
            first_position = edges.targets[0].position
            second_position = edges.targets[1].position

        builder.add_cswap(controller_position.row, first_position.row, second_position.row)
        explored.add(controller_position)
        explored.add(first_position)
        explored.add(second_position)

    @staticmethod
    def _add_ccx_gate_to_circuit(data: CircuitPlacingData) -> None:
        builder, graph, explored, start = (
            data.circuit,
            data.graph,
            data.explored,
            data.start,
        )

        edges = graph.node_edge_data(start)
        is_target = edges.targets == []

        if is_target:
            first_controller_position = edges.controlled_by[0].position
            second_controller_position = edges.controlled_by[1].position
            target_position = start
        else:
            first_controller_position = start
            second_controller_position = edges.works_with[0].position
            target_position = edges.targets[0].position

        builder.add_ccx(
            first_controller_position.row,
            second_controller_position.row,
            target_position.row,
        )
        explored.add(first_controller_position)
        explored.add(second_controller_position)
        explored.add(target_position)
