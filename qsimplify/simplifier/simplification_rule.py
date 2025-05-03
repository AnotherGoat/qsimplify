from qsimplify.model import GateName, QuantumGraph


class SimplificationRule:
    def __init__(self, pattern: QuantumGraph, replacement: QuantumGraph) -> None:
        self.pattern = pattern
        self.replacement = replacement
        self._validate_graphs()
        self._fill_replacement()
        self._generate_mask()

    def _validate_graphs(self) -> None:
        if any(gate.name == GateName.MEASURE for gate in self.pattern):
            raise ValueError("Original pattern can't have measurement gates")

        if any(gate.name == GateName.MEASURE for gate in self.replacement):
            raise ValueError("Replacement pattern can't have measurement gates")

    def _fill_replacement(self) -> None:
        for position in self.pattern.iter_positions_by_row():
            if not self.replacement.has_node_at(position):
                self.replacement.add_node(GateName.ID, position)

    def _generate_mask(self) -> None:
        self.mask = {node.position: node.name != GateName.ID for node in self.replacement}

    def __str__(self) -> str:
        return f"Replace\n{self.pattern.draw_grid()}\nWith\n{self.replacement.draw_grid()}"
