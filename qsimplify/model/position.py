from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Represents a (row, column) position in a QuantumGraph. In the circuit, the row equals the qubit index."""

    row: int
    column: int

    def __post_init__(self):
        if self.row < 0 or self.column < 0:
            raise ValueError(f"Position '{self}' can't have negative coordinates")

    def __iter__(self):
        """Allows easy unpacking like row, column = position."""
        return iter((self.row, self.column))

    def __str__(self):
        return f"({self.row}, {self.column})"
