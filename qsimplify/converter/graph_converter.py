from abc import ABC, abstractmethod

from qsimplify.model import QuantumGraph


class GraphConverter[T](ABC):
    @abstractmethod
    def to_graph(self, data: T, clean_up: bool = True) -> QuantumGraph: ...

    @abstractmethod
    def from_graph(self, graph: QuantumGraph) -> T: ...
