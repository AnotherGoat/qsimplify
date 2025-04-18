from pydantic import ValidationError

from qsimplify.dto import QuantumGateAdapter

type Errors = dict[int, list[str]]


def validate_gates(gates: list[dict]) -> Errors:
    errors: Errors = {}

    for idx, gate_data in enumerate(gates):
        try:
            QuantumGateAdapter.validate_python(gate_data)
        except ValidationError as error:
            errors[idx] = _extract_messages(error)
        except Exception as error:
            errors[idx] = [f"unknown: {error}"]

    return errors


def _extract_messages(validation_error: ValidationError) -> list[str]:
    return [f"{error['loc'][-1]}: {error['msg']}" for error in validation_error.errors()]
