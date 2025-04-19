from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from qsimplify.model import QuantumGraph

T = TypeVar("T")


class GraphConverter(ABC, Generic[T]):
    @abstractmethod
    def to_graph(self, data: T) -> QuantumGraph: ...

    @abstractmethod
    def from_graph(self, graph: QuantumGraph) -> T: ...
