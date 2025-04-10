from qsimplify.model import GateName, QuantumGraph


class SimplificationRule:
    def __init__(self, pattern: QuantumGraph, replacement: QuantumGraph):
        self.pattern = pattern
        self.replacement = replacement
        self._fill_replacement()
        self._generate_mask()

    def _fill_replacement(self):
        for position in self.pattern.iter_positions_by_row():
            if not self.replacement.has_node_at(position):
                self.replacement.add_new_node(GateName.ID, position)

    def _generate_mask(self):
        self.mask = {
            node.position: node.name != GateName.ID for node in self.replacement
        }

    def __str__(self):
        return (
            f"Replace\n{self.pattern.draw_grid()}\nWith\n{self.replacement.draw_grid()}"
        )
