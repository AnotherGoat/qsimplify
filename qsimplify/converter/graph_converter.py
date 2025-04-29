from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from qsimplify.model import QuantumGraph

T = TypeVar("T")


class GraphConverter(ABC, Generic[T]):
    @abstractmethod
    def to_graph(self, data: T, clean_up: bool = True) -> QuantumGraph: ...

    @abstractmethod
    def from_graph(self, graph: QuantumGraph) -> T: ...
