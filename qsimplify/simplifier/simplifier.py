import itertools
from pathlib import Path

from qiskit import QuantumCircuit

from qsimplify.converter import Converter
from qsimplify.model import GateName, GraphNode, Position, QuantumGraph
from qsimplify.simplifier.graph_mappings import GraphMappings
from qsimplify.simplifier.rule_parser import RuleParser
from qsimplify.simplifier.simplification_rule import SimplificationRule
from qsimplify.utils import setup_logger


class Simplifier:
    _default_rules: list[SimplificationRule]

    def __init__(self, converter: Converter) -> None:
        self._logger = setup_logger("Simplifier")
        self._converter = converter

        parser = RuleParser()
        script_path = Path(__file__).parent
        default_rules_path = script_path / "default_rules.json5"

        self._default_rules = parser.load_rules_from_file(default_rules_path)

    def simplify_circuit(
        self,
        circuit: QuantumCircuit,
        add_build_steps: bool = False,
        circuit_name: str = "circuit",
    ) -> QuantumCircuit | tuple[QuantumCircuit, str]:
        graph = self._converter.circuit_to_graph(circuit)
        simplified_graph = self.simplify_graph(graph)
        return self._converter.graph_to_circuit(
            simplified_graph, add_build_steps=add_build_steps, circuit_name=circuit_name
        )

    def simplify_graph(
        self, graph: QuantumGraph, rules: list[SimplificationRule] | None = None
    ) -> QuantumGraph:
        if rules is None:
            rules = self._default_rules

        result = graph.copy()

        for rule in rules:
            self.apply_simplification_rule(result, rule)

        return result

    def apply_simplification_rule(self, graph: QuantumGraph, rule: SimplificationRule) -> None:
        self._logger.debug("Applying rule with mask %s", rule.mask)
        mappings = self.find_pattern(graph, rule.pattern, mask=rule.mask)

        while mappings is not None:
            self.replace_pattern(graph, rule.replacement, mappings)
            mappings = self.find_pattern(graph, rule.pattern, mask=rule.mask)

    def find_pattern(
        self,
        graph: QuantumGraph,
        pattern: QuantumGraph,
        mask: dict[Position, bool] | None = None,
    ) -> GraphMappings | None:
        pattern_start = self._find_start(pattern)
        self._logger.debug("Pattern start found at %s", pattern_start.position)

        for position in graph.iter_positions_by_row():
            self._logger.debug("Checking graph on position %s", position)
            node = graph[position]

            if not self._are_nodes_similar(node, pattern_start):
                self._logger.debug(
                    "No similarities found when comparing %s and %s",
                    node,
                    pattern_start,
                )
                continue

            mappings = self._match_pattern(graph, pattern, node, pattern_start, mask=mask)

            if mappings is not None:
                return mappings

        return None

    @staticmethod
    def _find_start(pattern: QuantumGraph) -> GraphNode:
        if pattern.height == 0:
            raise ValueError("Invalid pattern")

        for row_index in range(pattern.height):
            potential_start = pattern[Position(row_index, 0)]

            if potential_start is not None:
                return potential_start

        raise ValueError("Invalid pattern")

    @staticmethod
    def _are_nodes_similar(start: GraphNode, end: GraphNode) -> bool:
        return (
            start.name == end.name
            and start.rotation == end.rotation
            and start.measure_to == end.measure_to
        )

    def _match_pattern(
        self,
        graph: QuantumGraph,
        pattern: QuantumGraph,
        start: GraphNode,
        pattern_start: GraphNode,
        mask: dict[Position, bool] | None = None,
    ) -> GraphMappings | None:
        for row_permutation in self._calculate_row_permutations(
            graph, pattern, start, pattern_start
        ):
            self._logger.debug("Trying row permutation %s on start %s", row_permutation, start)
            subgraph, mappings = self.extract_subgraph(
                graph, row_permutation, start.position.column, pattern.width, mask=mask
            )

            if subgraph is not None and subgraph == pattern:
                self._logger.debug("Match found with mappings %s", mappings)
                return mappings

        self._logger.debug("No matches found")
        return None

    @staticmethod
    def _calculate_row_permutations(
        graph: QuantumGraph,
        pattern: QuantumGraph,
        start: GraphNode,
        pattern_start: GraphNode,
    ) -> list[list[int]]:
        pattern_height = pattern.height
        row = start.position.row

        if pattern_height == 1:
            return [[row]]

        other_rows = [row_index for row_index in range(graph.height) if row_index != row]
        permutations = [
            list(permutation)
            for permutation in itertools.permutations(other_rows, pattern.height - 1)
        ]

        for permutation in permutations:
            permutation.insert(pattern_start.position.row, row)

        return permutations

    def extract_subgraph(
        self,
        graph: QuantumGraph,
        rows: list[int],
        starting_column: int,
        width: int,
        mask: dict[Position, bool] | None = None,
    ) -> tuple[QuantumGraph | None, GraphMappings | None]:
        if len(rows) == 0 or width <= 0 or len(graph) == 0:
            raise ValueError("The graph, rows or width are invalid")

        if mask is None:
            mask = self._generate_full_mask(width, len(rows))

        mappings = self._extract_subgraph_mappings(graph, rows, starting_column, width, mask)
        self._logger.debug("Extracting mappings for width %s", width)

        if mappings is None:
            self._logger.debug("Mappings couldn't be extracted")
            return None, None

        subgraph = QuantumGraph()

        for old_position, new_position in mappings.items():
            node = graph[old_position]
            subgraph.add_new_node(
                node.name,
                new_position,
                rotation=node.rotation,
                measure_to=node.measure_to,
            )

            edges = [
                edge for edge in graph.node_edges(old_position) if not edge.name.is_positional()
            ]
            for edge in edges:
                subgraph.add_new_edge(
                    edge.name,
                    mappings[edge.start.position],
                    mappings[edge.end.position],
                )

        self._logger.debug("Mappings are valid, filling the subgraph")
        subgraph.fill_empty_spaces()
        subgraph.fill_positional_edges()
        return subgraph, mappings

    @staticmethod
    def _generate_full_mask(width: int, height: int) -> dict[Position, bool]:
        mask = {}

        for row in range(height):
            for column in range(width):
                position = Position(row, column)
                mask[position] = True

        return mask

    def _extract_subgraph_mappings(
        self,
        graph: QuantumGraph,
        rows: list[int],
        starting_column: int,
        width: int,
        mask: dict[Position, bool],
    ) -> GraphMappings | None:
        mappings: GraphMappings = {}
        self._logger.debug("Starting mapping extraction")

        for new_row, old_row in enumerate(rows):
            new_column = 0
            old_column = starting_column

            while True:
                if new_column == width:
                    break

                self._logger.debug(
                    "Trying to map %s into %s",
                    Position(old_row, old_column),
                    Position(new_row, new_column),
                )
                node = self._find_next_right_node(
                    graph,
                    Position(old_row, old_column),
                    not mask[Position(new_row, new_column)],
                )

                if node is None:
                    self._logger.debug("No node found at the right side")
                    return None

                mappings[node.position] = Position(new_row, new_column)
                self._logger.debug("Mappings updated to %s", mappings)
                old_column = node.position.column + 1
                new_column += 1

        for old_position in mappings:
            edges = [
                edge for edge in graph.node_edges(old_position) if not edge.name.is_positional()
            ]

            for edge in edges:
                if edge.end.position not in mappings:
                    return None

        return mappings

    def _find_next_right_node(
        self,
        graph: QuantumGraph,
        start: Position,
        can_be_identity: bool,
    ) -> GraphNode | None:
        edge_data = graph.node_edge_data(start)
        self._logger.debug("Going to the right starting from edge %s", edge_data)
        self._logger.debug("Can it be identity? %s", can_be_identity)

        if edge_data is None:
            self._logger.debug("No edge data found at position %s", start)
            return None

        while True:
            origin = edge_data.origin

            if can_be_identity or origin.name != GateName.ID:
                self._logger.debug("The origin %s can be accepted, finishing exploration", origin)
                return origin

            if edge_data.right is None:
                self._logger.debug("Reached the rightmost node, no origin found")
                return None

            edge_data = graph.node_edge_data(edge_data.right.position)

    def replace_pattern(
        self, graph: QuantumGraph, replacement: QuantumGraph, mappings: GraphMappings
    ) -> None:
        self._logger.debug("Removing nodes with mappings %s", mappings)
        for original_position in mappings:
            graph.clear_node(original_position)

        mappings = {key: value for key, value in mappings.items() if value is not None}
        reverse_mappings = self._invert_mappings(mappings)
        self._logger.debug("Reversed mappings are %s", reverse_mappings)

        for original, match in mappings.items():
            node = replacement[match]
            graph.add_new_node(
                node.name, original, rotation=node.rotation, measure_to=node.measure_to
            )

            for edge in replacement.node_edges(match):
                if edge.name.is_positional():
                    continue

                graph.add_new_edge(edge.name, original, reverse_mappings[edge.end.position])

        graph.fill_positional_edges()

    @staticmethod
    def _invert_mappings(mappings: GraphMappings) -> GraphMappings:
        return {value: key for key, value in mappings.items()}
