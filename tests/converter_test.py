from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import GateName

converter = Converter()
ID = GateName.ID
H = GateName.H
X = GateName.X
Y = GateName.Y
Z = GateName.Z
SWAP = GateName.SWAP
CH = GateName.CH
CX = GateName.CX
CZ = GateName.CZ
CCX = GateName.CCX
CSWAP = GateName.CSWAP

class TestConverter:
    @staticmethod
    def test_empty_circuit_to_graph():
        circuit = QuantumCircuit(2)
        graph = converter.circuit_to_graph(circuit)

        assert graph.width == 0
        assert graph.height == 0

    @staticmethod
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

        graph = converter.circuit_to_graph(circuit)

        assert graph[0, 0].name == H
        assert graph[0, 1].name == X
        assert graph[0, 2].name == Y
        assert graph[0, 3].name == Z
        assert graph[0, 4].name == X
        assert graph[0, 5].name == Z
        assert graph[0, 6].name == H
        assert graph[0, 7].name == Y

    @staticmethod
    def test_two_qubit_nodes():
        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.x(1)
        circuit.cx(0, 1)
        circuit.ch(1, 0)
        circuit.h(0)
        circuit.y(1)

        graph = converter.circuit_to_graph(circuit)

        assert graph[0, 0].name == H
        assert graph[1, 0].name == X

        assert graph[0, 1].name == CX
        assert graph[1, 1].name == CX

        assert graph[0, 2].name == CH
        assert graph[1, 2].name == CH

        assert graph[0, 3].name == H
        assert graph[1, 3].name == Y

    @staticmethod
    def test_qubit_placement():
        circuit = QuantumCircuit(3)

        circuit.cx(0, 1)
        circuit.h(0)
        circuit.x(0)
        circuit.y(1)
        circuit.z(2)
        circuit.h(0)
        circuit.h(0)
        circuit.ccx(0, 1, 2)
        circuit.x(0)
        circuit.y(1)
        circuit.z(2)

        graph = converter.circuit_to_graph(circuit)

        assert graph.width == 7

        assert graph[0, 1].name == H
        assert graph[0, 2].name == X
        assert graph[1, 1].name == Y
        assert graph[1, 2].name == ID
        assert graph[2, 0].name == Z
        assert graph[2, 1].name == ID
        assert graph[2, 2].name == ID

        assert graph[1, 3].name == ID
        assert graph[2, 3].name == ID
        assert graph[1, 4].name == ID
        assert graph[2, 4].name == ID

        assert graph[0, 6].name == X
        assert graph[1, 6].name == Y
        assert graph[2, 6].name == Z

    @staticmethod
    def test_horizontal_edges():
        circuit = QuantumCircuit(1)

        circuit.h(0)
        circuit.x(0)
        circuit.z(0)

        graph = converter.circuit_to_graph(circuit)

        edge_1 = graph.find_edges(0, 0)
        assert edge_1.left is None
        assert edge_1.right.name == X

        edge_2 = graph.find_edges(0, 1)
        assert edge_2.left.name == H
        assert edge_2.right.name == Z

        edge_3 = graph.find_edges(0, 2)
        assert edge_3.left.name == X
        assert edge_3.right is None

    @staticmethod
    def test_vertical_edges():
        circuit = QuantumCircuit(3)

        circuit.h(0)
        circuit.x(1)
        circuit.z(2)

        graph = converter.circuit_to_graph(circuit)

        h_edges = graph.find_edges(0, 0)
        assert h_edges.up is None
        assert h_edges.down.name == X

        x_edges = graph.find_edges(1, 0)
        assert x_edges.up.name == H
        assert x_edges.down.name == Z

        z_edges = graph.find_edges(2, 0)
        assert z_edges.up.name == X
        assert z_edges.down is None

    @staticmethod
    def test_control_edges():
        circuit = QuantumCircuit(3)

        circuit.cz(1, 0)
        circuit.ccx(1, 2, 0)

        graph = converter.circuit_to_graph(circuit)

        cz_edges_0 = graph.find_edges(0, 0)
        assert cz_edges_0.targets == []
        assert cz_edges_0.controlled_by[0].name == CZ
        assert cz_edges_0.works_with == []
        cz_edges_1 = graph.find_edges(1, 0)
        assert cz_edges_1.targets[0].name == CZ
        assert cz_edges_1.controlled_by == []
        assert cz_edges_1.works_with == []

        ccx_edges_0 = graph.find_edges(0, 1)
        assert ccx_edges_0.targets == []
        assert ccx_edges_0.controlled_by[0].name == CCX
        assert ccx_edges_0.controlled_by[1].name == CCX
        assert ccx_edges_0.works_with == []
        ccx_edges_1 = graph.find_edges(1, 1)
        assert ccx_edges_1.targets[0].name == CCX
        assert ccx_edges_1.controlled_by == []
        assert ccx_edges_1.works_with[0].name == CCX
        ccx_edges_2 = graph.find_edges(2, 1)
        assert ccx_edges_2.targets[0].name == CCX
        assert ccx_edges_2.controlled_by == []
        assert ccx_edges_2.works_with[0].name == CCX


    @staticmethod
    def test_swap_edges():
        circuit = QuantumCircuit(3)

        circuit.swap(1, 2)
        circuit.cswap(0, 1, 2)

        graph = converter.circuit_to_graph(circuit)

        swap_edges_1 = graph.find_edges(1, 0)
        assert swap_edges_1.targets == []
        assert swap_edges_1.controlled_by == []
        assert swap_edges_1.swaps_with.name == SWAP
        swap_edges_2 = graph.find_edges(2, 0)
        assert swap_edges_2.targets == []
        assert swap_edges_2.controlled_by == []
        assert swap_edges_2.swaps_with.name == SWAP

        cswap_edges_0 = graph.find_edges(0, 1)
        assert cswap_edges_0.targets[0].name == CSWAP
        assert cswap_edges_0.targets[1].name == CSWAP
        assert cswap_edges_0.controlled_by == []
        cswap_edges_1 = graph.find_edges(1, 1)
        assert cswap_edges_1.targets == []
        assert cswap_edges_1.controlled_by[0].name == CSWAP
        assert cswap_edges_1.swaps_with.name == CSWAP
        cswap_edges_2 = graph.find_edges(2, 1)
        assert cswap_edges_2.targets == []
        assert cswap_edges_2.controlled_by[0].name == CSWAP
        assert cswap_edges_2.swaps_with.name == CSWAP

    @staticmethod
    def test_one_qubit_to_circuit():
        circuit = QuantumCircuit(1)

        circuit.h(0)
        circuit.x(0)
        circuit.y(0)
        circuit.z(0)
        circuit.x(0)
        circuit.z(0)
        circuit.h(0)
        circuit.y(0)

        graph = converter.circuit_to_graph(circuit)
        converted_circuit = converter.graph_to_circuit(graph)

        assert circuit.data == converted_circuit.data

    @staticmethod
    def test_two_qubits_to_circuit():
        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.x(1)
        circuit.cx(0, 1)
        circuit.ch(1, 0)
        circuit.cz(0, 1)
        circuit.y(0)
        circuit.z(1)

        graph = converter.circuit_to_graph(circuit)
        converted_circuit = converter.graph_to_circuit(graph)

        assert circuit.data == converted_circuit.data

    @staticmethod
    def test_removed_identities():
        circuit = QuantumCircuit(5)

        circuit.id(0)
        circuit.id(1)
        circuit.id(2)

        graph = converter.circuit_to_graph(circuit)
        converted_circuit = converter.graph_to_circuit(graph)

        assert circuit.data != converted_circuit.data
        assert len(converted_circuit.data) == 0
