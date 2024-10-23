from qsimplify.model import QuantumGraph


class SimplificationRule:
    def __init__(self, pattern: QuantumGraph, replacement: QuantumGraph):
        self.pattern = pattern
        self.replacement = replacement
