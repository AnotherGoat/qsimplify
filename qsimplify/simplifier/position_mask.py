from typing import override

from qsimplify.model import Position


class PositionMask:
    """A mask for a simplification rule, where each position is mapped to a boolean value."""

    _data: dict[Position, bool]

    def __init__(self, data: dict[Position, bool]) -> None:
        """Create a new mask."""
        self._data = data

    def is_set(self, position: Position) -> bool:
        """Check whether a position is set in this mask or not."""
        return self._data[position]

    @override
    def __str__(self) -> str:
        """Get a string representation of this mask."""
        joined_values = ", ".join(
            f"T{key}" if value else f"F{key}" for key, value in self._data.items()
        )
        return f"[{joined_values}]"

    @override
    def __eq__(self, other: object) -> bool:
        """Check whether this mask is equal to another mask. Fails automatically if other is not a position mask."""
        if not isinstance(other, PositionMask):
            return NotImplemented

        return self._data == other._data
