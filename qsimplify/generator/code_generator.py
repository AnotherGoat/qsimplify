from abc import ABC, abstractmethod

from qsimplify.model import QuantumGraph


class CodeGenerator(ABC):
    """Generates code that can build the quantum circuit represented by a graph."""

    @abstractmethod
    def generate(self, graph: QuantumGraph) -> str:
        """Generate code based on the provided graph."""
        ...
