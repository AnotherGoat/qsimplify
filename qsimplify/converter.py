from typing import Callable, Tuple
from qiskit import QuantumCircuit
from typing_extensions import NamedTuple

from qsimplify.model import QuantumGraph, Position, EdgeName, GateName, GraphNode
from qsimplify.utils import find_qubit_indexes, setup_logger, find_bit_indexes

class GraphPlacingData(NamedTuple):
    graph: QuantumGraph
    gate_name: GateName
    qubits: list[int]
    bits: list[int]
    params: list
    column: int

class CircuitPlacingData(NamedTuple):
    graph: QuantumGraph
    graph_node: GraphNode
    build_steps: list[str]
    explored: set[Position]
    start: Position

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

            if gate_name in (GateName.ID, GateName.BARRIER):
                continue

            qubits = find_qubit_indexes(circuit, instruction)
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

            bits = find_bit_indexes(circuit, instruction)
            params = instruction.operation.params
            placing_data = GraphPlacingData(graph, gate_name, qubits, bits, params, target_column)
            self._add_instruction_to_graph(placing_data)

        self.logger.debug("This is the graph before filling empty spaces\n%s", graph)
        graph.fill_empty_spaces()
        self.logger.debug("This is the graph before adding positional edges\n%s", graph)
        graph.fill_positional_edges()
        self.logger.debug("After adding all the edges, this is the result\n%s", graph)
        self.logger.debug("For comparison, this is the original circuit\n%s", circuit.draw())
        return graph


    def _add_instruction_to_graph(self, data: GraphPlacingData):
        if data.gate_name == GateName.MEASURE:
            self._add_measure_gate_to_graph(data)
            return

        if data.gate_name in [GateName.RX, GateName.RY, GateName.RZ]:
            self._add_rotation_gate_to_graph(data)
            return

        if len(data.qubits) == 1:
            self._add_single_qubit_gate_to_graph(data)
            return

        match data.gate_name:
            case GateName.SWAP:
                self._add_swap_gate_to_graph(data)
            case GateName.CSWAP:
                self._add_cswap_gate_to_graph(data)
            case _:
                self._add_controlled_gate_to_graph(data)

    def _add_measure_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, bits, _, column = data
        qubit = qubits[0]
        bit = bits[0]

        self.logger.debug("Placing measure gate on qubit %s to bit %s on column %s", qubit, bit, column)
        graph.add_new_node(gate_name, (qubit, column), measure_to=bit)

    def _add_rotation_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, _, params, column = data
        qubit = qubits[0]
        angle = params[0]

        self.logger.debug("Placing rotation gate with angle %s on qubit %s on column %s", angle, qubit, column)
        graph.add_new_node(gate_name, (qubit, column), rotation=angle)

    def _add_single_qubit_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, _, _, column = data
        qubit = qubits[0]

        self.logger.debug("Placing single-qubit gate on qubit %s on column %s", qubit, column)
        graph.add_new_node(gate_name, (qubit, column))

    def _add_swap_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, _, _, column = data
        first_position = (qubits[0], column)
        second_position = (qubits[1], column)

        self.logger.debug("Placing swap gate on qubits %s and %s on column %s", qubits[0], qubits[1], column)
        graph.add_new_node(gate_name, first_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, first_position, second_position)

        graph.add_new_node(gate_name, second_position)
        graph.add_new_edge(EdgeName.SWAPS_WITH, second_position, first_position)

    def _add_cswap_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, _, _, column = data
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

    def _add_controlled_gate_to_graph(self, data: GraphPlacingData):
        graph, gate_name, qubits, _, _, column = data
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


    def graph_to_circuit(self, graph: QuantumGraph, add_build_steps=False) -> QuantumCircuit | Tuple[QuantumCircuit, list[str]]:
        self.logger.debug("Converting graph to circuit")
        circuit = QuantumCircuit(graph.height)
        build_steps = [f"circuit = QuantumCircuit({graph.height})"]
        explored: set[Position] = set()

        for column_index in range(graph.width):
            for row_index in range(graph.height):
                position = (row_index, column_index)
                self._add_to_circuit(graph, circuit, build_steps, explored, position)

        if add_build_steps:
            return circuit, build_steps

        return circuit

    def _add_to_circuit(self, graph: QuantumGraph, circuit: QuantumCircuit, build_steps: list[str], explored: set[Position], position: Position):
        if position in explored:
            return

        explored.add(position)
        graph_node = graph[*position]

        if graph_node is None or graph_node.name == GateName.ID:
            return

        placing_data = CircuitPlacingData(graph, graph_node, build_steps, explored, position)
        add_instructions = {
            GateName.H: (self._add_single_qubit_gate_to_circuit, circuit.h),
            GateName.X: (self._add_single_qubit_gate_to_circuit, circuit.x),
            GateName.Y: (self._add_single_qubit_gate_to_circuit, circuit.y),
            GateName.Z: (self._add_single_qubit_gate_to_circuit, circuit.z),
            GateName.RX: (self._add_rotation_gate_to_circuit, circuit.rx),
            GateName.RY: (self._add_rotation_gate_to_circuit, circuit.ry),
            GateName.RZ: (self._add_rotation_gate_to_circuit, circuit.rz),
            GateName.SWAP: (self._add_swap_gate_to_circuit, circuit.swap),
            GateName.CH: (self._add_controlled_gate_to_circuit, circuit.ch),
            GateName.CX: (self._add_controlled_gate_to_circuit, circuit.cx),
            GateName.CZ: (self._add_controlled_gate_to_circuit, circuit.cz),
            GateName.CCX: (self._add_ccx_gate_to_circuit, circuit.ccx),
            GateName.CSWAP: (self._add_cswap_gate_to_circuit, circuit.cswap),
            GateName.MEASURE: (self._add_measure_gate_to_circuit, circuit.measure),
        }

        add_instruction, method = add_instructions.get(graph_node.name, (None, None))

        if add_instruction and method:
            add_instruction(placing_data, method)

    @staticmethod
    def _add_single_qubit_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        qubit = data.start[0]

        method(qubit)
        data.build_steps.append(f"circuit.{method.__name__}({qubit})")

    @staticmethod
    def _add_rotation_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        qubit = data.start[0]
        angle = data.graph_node.rotation

        method(angle, qubit)
        data.build_steps.append(f"circuit.{method.__name__}({angle}, {qubit})")

    @staticmethod
    def _add_swap_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        edges = data.graph.node_edge_data(*data.start)
        first_qubit = data.start[0]
        other_position = edges.swaps_with.position

        method(first_qubit, other_position[0])
        data.build_steps.append(f"circuit.{method.__name__}({first_qubit}, {other_position[0]})")
        data.explored.add(other_position)

    @staticmethod
    def _add_controlled_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        edges = data.graph.node_edge_data(*data.start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            target_position = data.start
        else:
            controller_position = data.start
            target_position = edges.targets[0].position

        method(controller_position[0], target_position[0])
        data.build_steps.append(f"circuit.{method.__name__}({controller_position[0]}, {target_position[0]})")
        data.explored.add(controller_position)
        data.explored.add(target_position)

    @staticmethod
    def _add_cswap_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        edges = data.graph.node_edge_data(*data.start)
        is_target = edges.targets == []

        if is_target:
            controller_position = edges.controlled_by[0].position
            first_position = data.start
            second_position = edges.swaps_with.position
        else:
            controller_position = data.start
            first_position = edges.targets[0].position
            second_position = edges.targets[1].position

        method(controller_position[0], first_position[0], second_position[0])
        data.build_steps.append(f"circuit.{method.__name__}({controller_position[0]}, {first_position[0]}, {second_position[0]})")
        data.explored.add(controller_position)
        data.explored.add(first_position)
        data.explored.add(second_position)

    @staticmethod
    def _add_ccx_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        edges = data.graph.node_edge_data(*data.start)
        is_target = edges.targets == []

        if is_target:
            first_controller_position = edges.controlled_by[0].position
            second_controller_position = edges.controlled_by[1].position
            target_position = data.start
        else:
            first_controller_position = data.start
            second_controller_position = edges.works_with[0].position
            target_position = edges.targets[0].position

        method(first_controller_position[0], second_controller_position[0], target_position[0])
        data.build_steps.append(f"circuit.{method.__name__}({first_controller_position[0]}, {second_controller_position[0]}, {target_position[0]})")
        data.explored.add(first_controller_position)
        data.explored.add(second_controller_position)
        data.explored.add(target_position)

    @staticmethod
    def _add_measure_gate_to_circuit(data: CircuitPlacingData, method: Callable):
        qubit = data.start[0]
        bit = data.graph_node.measure_to

        method(qubit, bit)
        data.build_steps.append(f"circuit.{method.__name__}({qubit}, {bit})")
