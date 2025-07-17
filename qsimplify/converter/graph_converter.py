"""Contains the base for converting graphs to and from other representations."""

from abc import ABC, abstractmethod

from qsimplify.model import QuantumGraph


class GraphConverter[T](ABC):
    """Converts a graph to and from T."""

    @abstractmethod
    def to_graph(self, data: T, clean_up: bool = True) -> QuantumGraph:
        """Convert a T object into a QuantumGraph.

        If clean_up is set to True, any empty rows and columns will be deleted.
        """
        ...

    @abstractmethod
    def from_graph(self, graph: QuantumGraph) -> T:
        """Convert a QuantumGraph into a T object."""
        ...
