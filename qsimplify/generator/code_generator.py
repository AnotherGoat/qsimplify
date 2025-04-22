from abc import ABC, abstractmethod

from qsimplify.model import QuantumGraph


class CodeGenerator(ABC):
    @abstractmethod
    def generate(self, graph: QuantumGraph) -> str: ...
