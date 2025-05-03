from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Position:
    """
    Represents a (row, column) position in a QuantumGraph.

    Attributes:
        row: The row, equivalent to the qubit index. Cannot be negative.
        column: The column index. Cannot be negative.
    """

    row: int
    column: int

    def __post_init__(self) -> None:
        """Check that the position's coordinates are valid."""
        if self.row < 0 or self.column < 0:
            raise ValueError(f"Position '{self}' can't have negative coordinates")

    def __iter__(self) -> Iterator[int]:
        """Iterate over the position's coordinates, first the row and then the column.

        Also allows to unpack this position in an easy to use way, like: row, column = position.
        """
        return iter((self.row, self.column))

    def __str__(self) -> str:
        """Get a string representation of this position."""
        return f"({self.row}, {self.column})"
