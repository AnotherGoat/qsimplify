import math

import pytest

from qsimplify.model.quantum_gate import (
    CcxGate,
    CczGate,
    ChGate,
    CswapGate,
    CxGate,
    CyGate,
    CzGate,
    GatesValidationError,
    HGate,
    IdGate,
    MeasureGate,
    RxGate,
    RyGate,
    RzGate,
    SdgGate,
    SGate,
    SwapGate,
    SxGate,
    SyGate,
    TdgGate,
    TGate,
    XGate,
    YGate,
    ZGate,
    parse_gates,
)

ANGLE_REQUIRED = "angle: Field required"
ANGLE_FINITE = "angle: It must be a finite number (not Inf or NaN)"
QUBIT_REQUIRED = "qubit: Field required"
QUBIT_POSITIVE = "qubit: It must be 0 or positive"
QUBIT2_REQUIRED = "qubit2: Field required"
QUBIT3_REQUIRED = "qubit3: Field required"
CONTROL_REQUIRED = "control_qubit: Field required"
CONTROL2_REQUIRED = "control_qubit2: Field required"
TARGET_REQUIRED = "target_qubit: Field required"
TARGET2_REQUIRED = "target_qubit2: Field required"


def test_parse_missing_name():
    gates = [
        {"qubit": 0},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {0: ["name: Field required"]}


def test_parse_unknown_gate():
    gates = [
        {"name": "what", "qubit": 0},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {0: ["name: It must be a supported gate name"]}


def test_parse_missing_single_qubit_gates():
    gates = [
        {"name": "id"},
        {"name": "h"},
        {"name": "x"},
        {"name": "y"},
        {"name": "z"},
        {"name": "s"},
        {"name": "sdg"},
        {"name": "sx"},
        {"name": "sy"},
        {"name": "t"},
        {"name": "tdg"},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert len(errors) == len(gates)
    assert all(messages == [QUBIT_REQUIRED] for messages in errors.values())


def test_parse_missing_rotation_gates():
    gates = [
        {"name": "rx", "qubit": 0},
        {"name": "rx", "angle": 0.1},
        {"name": "ry", "qubit": 1},
        {"name": "ry", "angle": 0.5},
        {"name": "rz", "qubit": 2},
        {"name": "rz", "angle": 1},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: [ANGLE_REQUIRED],
        1: [QUBIT_REQUIRED],
        2: [ANGLE_REQUIRED],
        3: [QUBIT_REQUIRED],
        4: [ANGLE_REQUIRED],
        5: [QUBIT_REQUIRED],
    }


def test_parse_missing_measure_gates():
    gates = [
        {"name": "measure", "qubit": 0},
        {"name": "measure", "bit": 0},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: ["bit: Field required"],
        1: [QUBIT_REQUIRED],
    }


def test_parse_missing_two_qubit_gates():
    gates = [
        {"name": "swap", "qubit": 0},
        {"name": "swap", "qubit2": 1},
        {"name": "ch", "control_qubit": 1},
        {"name": "ch", "target_qubit": 2},
        {
            "name": "cx",
            "control_qubit": 0,
        },
        {"name": "cx", "target_qubit": 1},
        {"name": "cy", "control_qubit": 1},
        {"name": "cy", "target_qubit": 2},
        {"name": "cz", "qubit": 2},
        {"name": "cz", "qubit2": 3},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: [QUBIT2_REQUIRED],
        1: [QUBIT_REQUIRED],
        2: [TARGET_REQUIRED],
        3: [CONTROL_REQUIRED],
        4: [TARGET_REQUIRED],
        5: [CONTROL_REQUIRED],
        6: [TARGET_REQUIRED],
        7: [CONTROL_REQUIRED],
        8: [QUBIT2_REQUIRED],
        9: [QUBIT_REQUIRED],
    }


def test_parse_missing_three_qubit_gates():
    gates = [
        {"name": "cswap", "control_qubit": 0},
        {"name": "cswap", "target_qubit": 1},
        {"name": "cswap", "target_qubit2": 2},
        {"name": "ccx", "control_qubit": 0},
        {"name": "ccx", "control_qubit2": 2},
        {"name": "ccx", "target_qubit": 1},
        {"name": "ccz", "qubit": 0},
        {"name": "ccz", "qubit2": 1},
        {"name": "ccz", "qubit3": 2},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: [TARGET_REQUIRED, TARGET2_REQUIRED],
        1: [CONTROL_REQUIRED, TARGET2_REQUIRED],
        2: [CONTROL_REQUIRED, TARGET_REQUIRED],
        3: [CONTROL2_REQUIRED, TARGET_REQUIRED],
        4: [CONTROL_REQUIRED, TARGET_REQUIRED],
        5: [CONTROL_REQUIRED, CONTROL2_REQUIRED],
        6: [QUBIT2_REQUIRED, QUBIT3_REQUIRED],
        7: [QUBIT_REQUIRED, QUBIT3_REQUIRED],
        8: [QUBIT_REQUIRED, QUBIT2_REQUIRED],
    }


def test_parse_shows_correct_indices():
    gates = [
        {"name": "id", "qubit": 0},
        {"name": "h"},
        {"name": "x", "qubit": 0},
        {"name": "y", "qubit": 0},
        {"name": "z"},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        1: [QUBIT_REQUIRED],
        4: [QUBIT_REQUIRED],
    }


def test_parse_extra_fields():
    gates = [
        {"name": "h", "qubit": 0, "qubit2": 1},
        {"name": "x", "qubit": 0, "angle": 0.1, "unknown": []},
        {"name": "rx", "qubit": 0, "angle": 0.1, "bit": 0, "target_qubit": 1},
        {"name": "ccx", "control_qubit": 0, "control_qubit2": 1, "target_qubit": 2, "???": -1},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: ["qubit2: Extra inputs are not permitted"],
        1: ["angle: Extra inputs are not permitted", "unknown: Extra inputs are not permitted"],
        2: ["bit: Extra inputs are not permitted", "target_qubit: Extra inputs are not permitted"],
        3: ["???: Extra inputs are not permitted"],
    }


def test_parse_negative_qubits():
    gates = [
        {"name": "z", "qubit": -3},
        {"name": "rz", "qubit": -2, "angle": 1},
        {"name": "measure", "qubit": -2, "bit": 1},
        {"name": "swap", "qubit": 0, "qubit2": -1},
        {"name": "ch", "control_qubit": -1, "target_qubit": 2},
        {"name": "cswap", "control_qubit": 0, "target_qubit": 1, "target_qubit2": -2},
        {"name": "ccx", "control_qubit": 0, "control_qubit2": -2, "target_qubit": 1},
        {"name": "ccz", "qubit": 0, "qubit2": 1, "qubit3": -2},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: [QUBIT_POSITIVE],
        1: [QUBIT_POSITIVE],
        2: [QUBIT_POSITIVE],
        3: ["qubit2: It must be 0 or positive"],
        4: ["control_qubit: It must be 0 or positive"],
        5: ["target_qubit2: It must be 0 or positive"],
        6: ["control_qubit2: It must be 0 or positive"],
        7: ["qubit3: It must be 0 or positive"],
    }


def test_parse_negative_bits():
    gates = [
        {"name": "measure", "qubit": 0, "bit": -1},
        {"name": "measure", "qubit": 3, "bit": -3},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: ["bit: It must be 0 or positive"],
        1: ["bit: It must be 0 or positive"],
    }


def test_parse_unexpected_angles():
    gates = [
        {"name": "rz", "qubit": 3, "angle": math.inf},
        {"name": "ry", "qubit": 2, "angle": -math.inf},
        {"name": "rz", "qubit": 1, "angle": math.nan},
        {"name": "ry", "qubit": 0, "angle": -math.nan},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: [ANGLE_FINITE],
        1: [ANGLE_FINITE],
        2: [ANGLE_FINITE],
        3: [ANGLE_FINITE],
    }


def test_parse_repeated_qubits():
    gates = [
        {"name": "swap", "qubit": 1, "qubit2": 1},
        {"name": "ch", "control_qubit": 2, "target_qubit": 2},
        {"name": "cx", "control_qubit": 1, "target_qubit": 1},
        {"name": "cy", "control_qubit": 0, "target_qubit": 0},
        {"name": "cz", "qubit": 3, "qubit2": 3},
        {"name": "cswap", "control_qubit": 0, "target_qubit": 0, "target_qubit2": 2},
        {"name": "ccx", "control_qubit": 0, "control_qubit2": 2, "target_qubit": 2},
        {"name": "ccz", "qubit": 2, "qubit2": 2, "qubit3": 2},
    ]

    with pytest.raises(GatesValidationError) as error:
        parse_gates(gates)

    errors = error.value.errors

    assert errors == {
        0: ["swap: Fields qubit and qubit2 must be different"],
        1: ["ch: Fields control_qubit and target_qubit must be different"],
        2: ["cx: Fields control_qubit and target_qubit must be different"],
        3: ["cy: Fields control_qubit and target_qubit must be different"],
        4: ["cz: Fields qubit and qubit2 must be different"],
        5: ["cswap: Fields control_qubit, target_qubit and target_qubit2 must be different"],
        6: ["ccx: Fields control_qubit, control_qubit2 and target_qubit must be different"],
        7: ["ccz: Fields qubit, qubit2 and qubit3 must be different"],
    }


def test_parse_valid_single_qubit_gates():
    gates = [
        {"name": "id", "qubit": 0},
        {"name": "h", "qubit": 0},
        {"name": "x", "qubit": 1},
        {"name": "y", "qubit": 2},
        {"name": "z", "qubit": 3},
        {"name": "s", "qubit": 0},
        {"name": "sdg", "qubit": 2},
        {"name": "sx", "qubit": 4},
        {"name": "sy", "qubit": 6},
        {"name": "t", "qubit": 8},
        {"name": "tdg", "qubit": 10},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        IdGate(qubit=0),
        HGate(qubit=0),
        XGate(qubit=1),
        YGate(qubit=2),
        ZGate(qubit=3),
        SGate(qubit=0),
        SdgGate(qubit=2),
        SxGate(qubit=4),
        SyGate(qubit=6),
        TGate(qubit=8),
        TdgGate(qubit=10),
    ]


def test_parse_valid_rotation_gates():
    gates = [
        {"name": "rx", "qubit": 0, "angle": 0.1},
        {"name": "ry", "qubit": 1, "angle": 0.5},
        {"name": "rz", "qubit": 2, "angle": 1},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        RxGate(qubit=0, angle=0.1),
        RyGate(qubit=1, angle=0.5),
        RzGate(qubit=2, angle=1),
    ]


def test_parse_valid_measure_gates():
    gates = [
        {"name": "measure", "qubit": 0, "bit": 0},
        {"name": "measure", "qubit": 1, "bit": 2},
        {"name": "measure", "qubit": 2, "bit": 1},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        MeasureGate(qubit=0, bit=0),
        MeasureGate(qubit=1, bit=2),
        MeasureGate(qubit=2, bit=1),
    ]


def test_parse_valid_two_qubit_gates():
    gates = [
        {"name": "swap", "qubit": 0, "qubit2": 1},
        {"name": "ch", "control_qubit": 1, "target_qubit": 2},
        {"name": "cx", "control_qubit": 0, "target_qubit": 1},
        {"name": "cy", "control_qubit": 1, "target_qubit": 2},
        {"name": "cz", "qubit": 2, "qubit2": 3},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        SwapGate(qubit=0, qubit2=1),
        ChGate(control_qubit=1, target_qubit=2),
        CxGate(control_qubit=0, target_qubit=1),
        CyGate(control_qubit=1, target_qubit=2),
        CzGate(qubit=2, qubit2=3),
    ]


def test_parse_valid_three_qubit_gates():
    gates = [
        {"name": "cswap", "control_qubit": 0, "target_qubit": 1, "target_qubit2": 2},
        {"name": "ccx", "control_qubit": 0, "control_qubit2": 2, "target_qubit": 1},
        {"name": "ccz", "qubit": 0, "qubit2": 1, "qubit3": 2},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        CswapGate(control_qubit=0, target_qubit=1, target_qubit2=2),
        CcxGate(control_qubit=0, control_qubit2=2, target_qubit=1),
        CczGate(qubit=0, qubit2=1, qubit3=2),
    ]


def test_parse_empty_gates():
    gates = []
    parsed_gates = parse_gates(gates)
    assert parsed_gates == []


def test_parse_gate_aliases():
    gates = [
        {"name": "i", "qubit": 0},
        {"name": "not", "qubit": 1},
        {"name": "sz", "qubit": 0},
        {"name": "sqrtz", "qubit": 1},
        {"name": "sd", "qubit": 2},
        {"name": "szd", "qubit": 3},
        {"name": "szdg", "qubit": 4},
        {"name": "sqrtzd", "qubit": 5},
        {"name": "sqrtzdg", "qubit": 6},
        {"name": "sqrtx", "qubit": 2},
        {"name": "sqrty", "qubit": 4},
        {"name": "td", "qubit": 7},
        {"name": "cnot", "control_qubit": 0, "target_qubit": 1},
        {"name": "fredkin", "control_qubit": 0, "target_qubit": 1, "target_qubit2": 2},
        {"name": "ccnot", "control_qubit": 3, "control_qubit2": 1, "target_qubit": 2},
        {"name": "toffoli", "control_qubit": 0, "control_qubit2": 2, "target_qubit": 1},
    ]

    parsed_gates = parse_gates(gates)

    assert parsed_gates == [
        IdGate(qubit=0),
        XGate(qubit=1),
        SGate(qubit=0),
        SGate(qubit=1),
        SdgGate(qubit=2),
        SdgGate(qubit=3),
        SdgGate(qubit=4),
        SdgGate(qubit=5),
        SdgGate(qubit=6),
        SxGate(qubit=2),
        SyGate(qubit=4),
        TdgGate(qubit=7),
        CxGate(control_qubit=0, target_qubit=1),
        CswapGate(control_qubit=0, target_qubit=1, target_qubit2=2),
        CcxGate(control_qubit=3, control_qubit2=1, target_qubit=2),
        CcxGate(control_qubit=0, control_qubit2=2, target_qubit=1),
    ]
