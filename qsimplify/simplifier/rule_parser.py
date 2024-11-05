from typing import Any, NamedTuple, Callable

import json5
from qsimplify.model import GraphBuilder, GateName
from qsimplify.simplifier.simplification_rule import SimplificationRule

class GatePlacingData(NamedTuple):
    builder: GraphBuilder
    gate_name: GateName
    extra_data: list[int | float]

class RuleParser:
    def __init__(self):
        self._gate_parsing_handlers: dict[GateName, Callable[[GatePlacingData], None]] = {
            GateName.H: self._add_single_gate,
            GateName.X: self._add_single_gate,
            GateName.Y: self._add_single_gate,
            GateName.Z: self._add_single_gate,
            GateName.RX: self._add_rotation_gate,
            GateName.RY: self._add_rotation_gate,
            GateName.RZ: self._add_rotation_gate,
            GateName.MEASURE: self._add_measure_gate,
            GateName.SWAP: self._add_swap_gate,
            GateName.CH: self._add_controlled_gate,
            GateName.CX: self._add_controlled_gate,
            GateName.CZ: self._add_cz_gate,
            GateName.CSWAP: self._add_cswap_gate,
            GateName.CCX: self._add_ccx_gate,
        }

    def load_rules_from_file(self, json5_path: str) -> list[SimplificationRule]:
        with open(json5_path, "r") as file:
            json_data = json5.load(file, allow_duplicate_keys=False)

        return self._parse_rules(json_data)

    def load_rules(self, json5_text: str) -> list[SimplificationRule]:
        json_data = json5.loads(json5_text, allow_duplicate_keys=False)
        return self._parse_rules(json_data)

    def _parse_rules(self, json_data: Any) -> list[SimplificationRule]:
        rules = []

        for rule_data in json_data:
            rules.append(self._parse_rule(rule_data))

        return rules

    def _parse_rule(self, rule_data: Any) -> SimplificationRule:
        if "pattern" not in rule_data or "replacement" not in rule_data:
            raise ValueError(f"The rule {rule_data} is missing its pattern or replacement keys")

        pattern = GraphBuilder()

        for gate_data in rule_data["pattern"]:
            self._parse_and_add_gate(pattern, gate_data)

        replacement = GraphBuilder()

        for gate_data in rule_data["replacement"]:
            self._parse_and_add_gate(replacement, gate_data)

        return SimplificationRule(pattern.build(), replacement.build())

    def _parse_and_add_gate(self, builder: GraphBuilder, gate_data: list[Any]):
        if not isinstance(gate_data[0], str):
            raise ValueError(f"The gate {gate_data} must have a string as its first element")

        gate_name = GateName.from_str(gate_data.pop(0))

        if len(gate_data) < 2:
            raise ValueError(f"The gate {gate_name}'s extra data {gate_data} must have at least 2 elements")

        if not self._all_numeric(gate_data):
            raise ValueError(f"The gate {gate_name}'s extra data {gate_data} must only have numbers")

        if gate_name in (GateName.ID, GateName.BARRIER):
            return

        placing_data = GatePlacingData(builder, gate_name, gate_data)
        self._gate_parsing_handlers[gate_name](placing_data)


    @staticmethod
    def _all_numeric(data: list[Any]) -> bool:
        return all(isinstance(item, (int, float)) for item in data)

    def _add_single_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int]):
            raise ValueError(f"The gate {gate_name}'s extra data {extra_data} must be [qubit: int, column: int]")

        builder.add_single(gate_name, extra_data[0], extra_data[1])

    def _add_rotation_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [float, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [angle: float, qubit: int, column: int]")

        builder.add_rotation(gate_name, extra_data[0], extra_data[1], extra_data[2])

    def _add_measure_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [qubit: int, bit: int, column: int]")

        builder.add_measure(extra_data[0], extra_data[1], extra_data[2])

    def _add_swap_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [qubit1: int, qubit2: int, column: int]")

        builder.add_swap(extra_data[0], extra_data[1], extra_data[2])

    def _add_controlled_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [control_qubit: int, target_qubit: int, column: int]")

        builder.add_control(gate_name, extra_data[0], extra_data[1], extra_data[2])

    def _add_cz_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [qubit1: int, qubit2: int, column: int]")

        builder.add_cz(extra_data[0], extra_data[1], extra_data[2])

    def _add_cswap_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [control_qubit: int, target_qubit1: int, target_qubit2: int, column: int]")

        builder.add_cswap(extra_data[0], extra_data[1], extra_data[2], extra_data[3])

    def _add_ccx_gate(self, data: GatePlacingData):
        builder, gate_name, extra_data = data

        if not self._check_types(extra_data, [int, int, int, int]):
            raise ValueError(
                f"The gate {gate_name}'s extra data {extra_data} must be [control_qubit1: int, control_qubit2: int, target_qubit: int, column: int]")

        builder.add_ccx(extra_data[0], extra_data[1], extra_data[2], extra_data[3])

    @staticmethod
    def _check_types(data: list[int | float], types: list[type]):
        if len(data) != len(types):
            return False

        return all(isinstance(item, item_type) for item, item_type in zip(data, types))
