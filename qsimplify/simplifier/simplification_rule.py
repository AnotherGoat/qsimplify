"""Contains the base for subgraph-based simplification rules."""

from qsimplify.model import GateName, QuantumGraph
from qsimplify.model.position import Position


class PositionMask:
    """A mask for a simplification rule, where each position is mapped to a boolean value."""

    _data: dict[Position, bool]

    def __init__(self, data: dict[Position, bool]) -> None:
        """Create a new mask."""
        self._data = data

    def is_set(self, position: Position) -> bool:
        """Check whether a position is set in this mask or not."""
        return self._data[position]

    def __str__(self) -> str:
        """Get a string representation of this mask."""
        joined_values = ", ".join(
            f"T{key}" if value else f"F{key}" for key, value in self._data.items()
        )
        return f"[{joined_values}]"

    def __eq__(self, other: object) -> bool:
        """Check whether this mask is equal to another mask. Fails automatically if other is not a position mask."""
        if not isinstance(other, PositionMask):
            return NotImplemented

        return self._data == other._data


class SimplificationRule:
    """A rule for simplifying a quantum graph, by replacing a pattern."""

    pattern: QuantumGraph
    replacement: QuantumGraph
    mask: PositionMask

    def __init__(self, pattern: QuantumGraph, replacement: QuantumGraph) -> None:
        """Create a new simplification rule.

        Neither the pattern nor the replacement can have measurement gates.
        """
        self.pattern = pattern
        self.replacement = replacement
        self._validate_graphs()
        self._fill_replacement()
        self._generate_mask()

    def _validate_graphs(self) -> None:
        if any(gate.name == GateName.MEASURE for gate in self.pattern):
            raise ValueError("Original pattern can't have measurement gates")

        if any(gate.name == GateName.MEASURE for gate in self.replacement):
            raise ValueError("Replacement pattern can't have measurement gates")

    def _fill_replacement(self) -> None:
        for position in self.pattern.iter_positions_by_row():
            if not self.replacement.has_node_at(position):
                self.replacement.add_node(GateName.ID, position)

    def _generate_mask(self) -> None:
        self.mask = PositionMask(
            {node.position: node.name != GateName.ID for node in self.replacement}
        )

    def __str__(self) -> str:
        """Get a string representation of this rule."""
        return f"Replace\n{self.pattern.draw_grid()}\nWith\n{self.replacement.draw_grid()}"
