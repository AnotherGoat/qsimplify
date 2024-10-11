from dataclasses import dataclass

from networkx.classes import MultiDiGraph

class GridNode:
    def __init__(self, name: str, targets = None, controlled_by = None):
        self.name = name
        self.targets = [] if targets is None else targets
        self.controlled_by = [] if controlled_by is None else controlled_by


    def __eq__(self, other) -> bool:
        if not isinstance(other, GridNode):
            return NotImplemented

        return self.name == other.name and self.targets == other.targets and self.controlled_by == other.controlled_by


    def __str__(self) -> str:
        name_data = f"name={self.name}"
        target_data = f"targets={self.targets}" if self.targets else ""
        controlled_by_data = f"controlled_by={self.controlled_by}" if self.controlled_by else ""
        non_empty_data = [data for data in [name_data, target_data, controlled_by_data] if data]
        return f"GridNode({', '.join(non_empty_data)})"


class QuantumGraph(MultiDiGraph):
    pass


@dataclass
class QuantumMetrics:
    # Circuit Size
    width: int = -1
    depth: int = -1

    # Circuit Density
    max_density: int = -1
    average_density: float = -1.0

    # Single-Qubit Gates
    pauli_x_count: int = -1
    pauli_y_count: int = -1
    pauli_z_count: int = -1
    pauli_count: int = -1
    hadamard_count: int = -1
    initial_superposition_rate: float = -1.0
    other_single_gates_count: int = -1
    single_gate_count: int = -1
    controlled_single_qubit_count: int = -1

    # All Gates in the Circuit
    gate_count: int = -1
    controlled_gate_count: int = -1
    single_gate_rate: float = -1.0
