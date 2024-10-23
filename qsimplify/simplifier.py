import itertools
from typing import TypeAlias

from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import QuantumGraph, GraphNode, GateName, Position, GraphBuilder
from qsimplify.utils import setup_logger

class SimplificationRule:
    def __init__(self, pattern: QuantumGraph, replacement: QuantumGraph):
        self.pattern = pattern
        self.replacement = replacement

_RULES: list[SimplificationRule] = []

pattern = GraphBuilder().add_h(0 ,0).add_h(0, 1).build()
replacement = GraphBuilder().add_id(0, 0).add_id(0, 1).build()
_RULES.append(SimplificationRule(pattern, replacement))

Mappings: TypeAlias = dict[Position, Position]

class Simplifier:
    def __init__(self, converter: Converter):
        self.logger = setup_logger("Simplifier")
        self.converter = converter

    def simplify_circuit(self, circuit: QuantumCircuit) -> QuantumCircuit:
        graph = self.converter.circuit_to_graph(circuit)
        simplified_graph = self.simplify_graph(graph)
        return self.converter.graph_to_circuit(simplified_graph)


    def simplify_graph(self, graph: QuantumGraph) -> QuantumGraph:
        result = graph.copy()

        for rule in _RULES:
            self.apply_simplify_rule(result, rule)

        return result


    def apply_simplify_rule(self, graph: QuantumGraph, rule: SimplificationRule):
        mappings = self.find_pattern(graph, rule.pattern)

        while mappings is not None:
            self.replace_pattern(graph, rule.replacement, mappings)
            mappings = self.find_pattern(graph, rule.pattern)


    def find_pattern(self, graph: QuantumGraph, pattern: QuantumGraph) -> Mappings | None:
        pattern_start = self._find_start(pattern)
        self.logger.debug("Pattern start found at %s", pattern_start.position)

        for row_index in range(graph.height):
            for column_index in range(graph.width):
                position = (row_index, column_index)
                self.logger.debug("Checking graph on position %s", position)
                node = graph[*position]

                if not self._are_nodes_similar(node, pattern_start):
                    self.logger.debug("No similarities found when comparing %s and %s", node, pattern_start)
                    continue

                mappings = self._match_pattern(graph, pattern, node, pattern_start)

                if mappings is not None:
                    return mappings

        return None


    def _find_start(self, pattern: QuantumGraph) -> GraphNode:
        if pattern.height == 0:
            raise ValueError("Invalid pattern")

        for row_index in range(pattern.height):
            potential_start = pattern[row_index, 0]

            if potential_start is not None:
                return potential_start

        raise ValueError("Invalid pattern")


    @staticmethod
    def _are_nodes_similar(start: GraphNode, end: GraphNode) -> bool:
        return start.name == end.name and start.rotation == end.rotation and start.measure_to == end.measure_to


    def _match_pattern(self, graph: QuantumGraph, pattern: QuantumGraph, start: GraphNode, pattern_start: GraphNode) -> Mappings | None:
        for row_permutation in self._calculate_row_permutations(graph, pattern, start, pattern_start):
            self.logger.debug("Trying row permutation %s on start %s", row_permutation, start)
            subgraph, mappings = self.extract_subgraph(graph, row_permutation, start.position[1], pattern.width)

            if subgraph is not None and subgraph == pattern:
                self.logger.debug("Match found with mappings %s", mappings)
                return mappings

        self.logger.debug("No matches found")
        return None


    @staticmethod
    def _calculate_row_permutations(graph: QuantumGraph, pattern: QuantumGraph, start: GraphNode, pattern_start: GraphNode) -> list[list[int]]:
        pattern_height = pattern.height
        row, column = start.position

        if pattern_height == 1:
            return [[row]]

        other_rows = [row_index for row_index in range(graph.height) if row_index != row]
        permutations = [list(permutation) for permutation in itertools.permutations(other_rows, pattern.height - 1)]

        for permutation in permutations:
            permutation.insert(pattern_start.position[0], row)

        return permutations


    def extract_subgraph(self, graph: QuantumGraph, rows: list[int], starting_column: int, width: int) -> tuple[QuantumGraph | None, Mappings | None]:
        if len(rows) == 0 or width <= 0 or len(graph) == 0:
            raise ValueError("The graph, rows or width are invalid")

        mappings = self._extract_subgraph_mappings(graph, rows, starting_column, width)

        if mappings is None:
            self.logger.debug("Mappings couldn't be extracted")
            return None, None

        subgraph = QuantumGraph()

        for old_position, new_position in mappings.items():
            node = graph[old_position]
            subgraph.add_new_node(node.name, new_position, rotation=node.rotation, measure_to=node.measure_to)

            edges = [edge for edge in graph.node_edges(*old_position) if not edge.name.is_positional()]
            for edge in edges:
                subgraph.add_new_edge(edge.name, mappings[edge.start.position], mappings[edge.end.position])

        self.logger.debug("Mappings are valid, filling the subgraph")
        subgraph.fill_empty_spaces()
        subgraph.fill_positional_edges()
        return subgraph, mappings

    def _extract_subgraph_mappings(self, graph: QuantumGraph, rows: list[int], starting_column: int, width: int) -> Mappings | None:
        mappings: Mappings = {}

        for (new_row, old_row) in enumerate(rows):
            new_column = 0
            old_column = starting_column

            while True:
                if new_column == width:
                    break

                node = self._find_next_right_node(graph, old_row, old_column)

                if node is None:
                    return None

                mappings[node.position] = (new_row, new_column)
                old_column = node.position[1] + 1
                new_column += 1

        for old_position in mappings.keys():
            edges = [edge for edge in graph.node_edges(*old_position) if not edge.name.is_positional()]

            for edge in edges:
                if edge.end.position not in mappings.keys():
                    return None

        return mappings


    @staticmethod
    def _find_next_right_node(graph: QuantumGraph, starting_row: int, starting_column: int) -> GraphNode | None:
        edge_data = graph.node_edge_data(starting_row, starting_column)

        if edge_data is None:
            return None

        while True:
            origin = edge_data.origin

            if origin.name != GateName.ID:
                return origin

            if edge_data.right is None:
                return None

            edge_data = graph.node_edge_data(*edge_data.right.position)


    @staticmethod
    def replace_pattern(graph: QuantumGraph, replacement: QuantumGraph, mappings: Mappings):
        for node in mappings.keys():
            graph.remove_node(node)

        reverse_mappings = {value: key for key, value in mappings.items()}

        for original, match in mappings.items():
            node = replacement[match]
            graph.add_new_node(node.name, original, rotation=node.rotation, measure_to=node.measure_to)

            for edge in replacement.node_edges(*match):
                if edge.name.is_positional():
                    continue

                graph.add_new_edge(edge.name, original, reverse_mappings[edge.end.position])

        graph.fill_positional_edges()
