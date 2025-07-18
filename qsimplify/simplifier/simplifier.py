import itertools
from pathlib import Path

from qsimplify import math_utils
from qsimplify.model import GateName, GraphNode, Position, QuantumGraph, graph_cleaner
from qsimplify.simplifier.graph_mappings import GraphMappings
from qsimplify.simplifier.rule_parser import RuleParser
from qsimplify.simplifier.simplification_rule import SimplificationRule
from qsimplify.utils import setup_logger


class Simplifier:
    """Simplifies a quantum graph using a set of rules."""

    _default_rules: list[SimplificationRule]

    def __init__(self) -> None:
        """Create a new simplifier."""
        self._logger = setup_logger("Simplifier")

        parser = RuleParser()
        script_path = Path(__file__).parent
        default_rules_path = script_path / "default_rules.json"

        self._default_rules = parser.load_rules_from_file(default_rules_path)

    def simplify_graph(
        self,
        graph: QuantumGraph,
        rules: list[SimplificationRule] | None = None,
        iterations: int = 1,
    ) -> QuantumGraph:
        """Simplify a quantum graph using a set of rules.

        A custom set of rules can be provided. If not, the default rules will be used.
        The graph will be cleaned up after applying all the rules.
        """
        if iterations <= 0:
            raise ValueError("Number of iterations must be greater than 0")

        if rules is None:
            rules = self._default_rules

        result = graph.copy()

        for _ in range(iterations):
            for rule in rules:
                self.apply_simplification_rule(result, rule)

            graph_cleaner.clean_and_fill(result)

        return result

    def apply_simplification_rule(self, graph: QuantumGraph, rule: SimplificationRule) -> None:
        """Apply a single simplification rule to a graph.

        Note that the graph is not cleaned up after the rule is applied.
        """
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
        """Try finding a pattern in a graph."""
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
            and Simplifier._are_angles_similar(start.angle, end.angle)
            and start.bit == end.bit
        )

    @staticmethod
    def _are_angles_similar(first: float | None, second: float | None) -> bool:
        """Check whether two angles are close enough to be considered equal."""
        if first is None and second is None:
            return True

        if first is None or second is None:
            return False

        return math_utils.are_floats_similar(first, second)

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
        if len(rows) == 0 or width <= 0 or graph.is_empty():
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
            subgraph.add_node(
                node.name,
                new_position,
                angle=node.angle,
                bit=node.bit,
            )

            edges = [
                edge for edge in graph.node_edges(old_position) if not edge.name.is_positional()
            ]
            for edge in edges:
                subgraph.add_edge(
                    edge.name,
                    mappings[edge.start.position],
                    mappings[edge.end.position],
                )

        self._logger.debug("Mappings are valid, filling the subgraph")
        graph_cleaner.clean_and_fill(subgraph)
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
            graph.add_node(node.name, original, angle=node.angle, bit=node.bit)

            for edge in replacement.node_edges(match):
                if edge.name.is_positional():
                    continue

                graph.add_edge(edge.name, original, reverse_mappings[edge.end.position])

        graph_cleaner.clean_and_fill(graph)

    @staticmethod
    def _invert_mappings(mappings: GraphMappings) -> GraphMappings:
        return {value: key for key, value in mappings.items()}
