"""Contains a data structure that stores graph patterns used for pattern matching."""

from typing import final

from loguru import logger

from qsimplify.model import GateName, GraphNode, Position, QuantumGraph


@final
class QuantumPattern(QuantumGraph):
    """A specialized type of quantum graph, used for pattern matching.

    It can't be empty or contain measurement gates.
    It also must have at least one node in the first column.
    """

    start: GraphNode
    """The starting, topmost and leftmost node of this pattern, found in its first column."""

    def __init__(self, graph: QuantumGraph) -> None:
        """Create a new pattern based on the given graph.

        A copy of the graph's data will be made during this process.
        """
        super().__init__()
        self._network = graph._network.copy()  # noqa: SLF001 (_network should be protected)
        self._validate()
        self._find_start()

    def _validate(self) -> None:
        """Check that the pattern is built correctly."""
        if self.is_empty():
            raise ValueError("Quantum pattern can't be empty")

        if any(gate.name == GateName.MEASURE for gate in self):
            raise ValueError("Quantum pattern can't have measurement gates")

    def _find_start(self) -> None:
        """Find the starting node of the original pattern."""
        for row_index in range(self.height):
            potential_start = self[Position(row_index, 0)]

            if potential_start is not None and potential_start.name != GateName.ID:
                logger.debug("Pattern start found at {}", potential_start.position)
                self.start = potential_start
                return

        raise ValueError(
            "The original pattern doesn't have valid starting point in its first column"
        )
