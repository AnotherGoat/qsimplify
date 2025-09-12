"""A controller for the /api/circuit endpoint."""

from http import HTTPStatus
from io import BytesIO
from typing import Generator

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from qsimplify import drawer
from qsimplify.analyzer import analyzer
from qsimplify.controller.dto import (
    DeltaMetricsResult,
    ErrorList,
    GateList,
    GateListErrors,
    GatesToCompare,
    GeneratedCode,
    MetricsResult,
    PlottingRequest,
    SimplificationRequest,
    SimplifiedCircuit,
)
from qsimplify.converter import GatesConverter, QiskitConverter
from qsimplify.generator import QiskitGenerator
from qsimplify.model.quantum_gate import CxGate, HGate, IdGate, XGate, YGate, ZGate
from qsimplify.simplifier import Simplifier

CHUNK_SIZE = 1024 * 8

circuit_router = APIRouter(prefix="/api/circuit")
gates_converter = GatesConverter()
qiskit_converter = QiskitConverter()
simplifier = Simplifier()
qiskit_generator = QiskitGenerator()

EXAMPLE_SIMPLIFICATION_REQUEST = Body(
    examples=[
        SimplificationRequest(
            gates=[
                CxGate(control_qubit=0, target_qubit=1),
                XGate(qubit=0),
                IdGate(qubit=1),
                IdGate(qubit=0),
                CxGate(control_qubit=0, target_qubit=1),
            ],
            iterations=3,
        )
    ]
)


@circuit_router.post(
    "/simplify",
    summary="Simplify a quantum circuit",
    description="Given a list of gates, the circuit will be simplified. The result will include the simplified circuit, metrics for circuits and generated code for building the simplified circuit.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"model": SimplifiedCircuit, "description": "The simplified circuit"},
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _simplify_circuit(
    dto: SimplificationRequest = EXAMPLE_SIMPLIFICATION_REQUEST,
) -> SimplifiedCircuit:
    graph = gates_converter.to_graph(dto.gates)
    simplified_graph = simplifier.simplify_graph(graph, iterations=dto.iterations)
    simplified_gates = gates_converter.from_graph(simplified_graph)
    original_metrics = analyzer.calculate_metrics(graph)
    new_metrics = analyzer.calculate_metrics(simplified_graph)
    delta_metrics = analyzer.compare_metrics(graph, simplified_graph)
    build_steps = qiskit_generator.generate(graph)

    return SimplifiedCircuit(
        gates=GateList(gates=simplified_gates),
        original_metrics=original_metrics,
        new_metrics=new_metrics,
        delta_metrics=delta_metrics,
        code=build_steps,
    )


EXAMPLE_PLOTTING_REQUEST = Body(
    examples=[
        PlottingRequest(
            gates=[
                XGate(qubit=0),
                YGate(qubit=0),
                ZGate(qubit=0),
            ],
            dpi=300,
        )
    ]
)


def _generate_stream(buffer: BytesIO) -> Generator[bytes, None, None]:
    buffer.seek(0)

    while True:
        chunk = buffer.read(CHUNK_SIZE)

        if not chunk:
            break

        yield chunk


@circuit_router.post(
    "/plot",
    summary="Plot a quantum circuit, using the Qiskit library",
    description="Given a list of gates, a PNG image of the circuit will be returned. Identity gates will be skipped.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"content": {"image/png": {}}, "description": "A PNG image of the circuit."},
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _plot_circuit(dto: PlottingRequest = EXAMPLE_PLOTTING_REQUEST) -> StreamingResponse:
    graph = gates_converter.to_graph(dto.gates)
    qiskit_circuit = qiskit_converter.from_graph(graph)
    buffer = drawer.save_circuit_to_buffer(qiskit_circuit, dpi=dto.dpi)
    return StreamingResponse(_generate_stream(buffer), media_type="image/png")


@circuit_router.post(
    "/plot_graph",
    summary="Plot a quantum graph representation of a quantum circuit",
    description="Given a list of gates, a PNG image of the graph representation will be returned. Identity gates will be skipped where possible.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {
            "content": {"image/png": {}},
            "description": "A PNG image of the graph representation.",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _plot_graph(dto: PlottingRequest = EXAMPLE_PLOTTING_REQUEST) -> StreamingResponse:
    graph = gates_converter.to_graph(dto.gates)
    buffer = drawer.save_graph_to_buffer(graph, "png", dpi=dto.dpi)
    return StreamingResponse(_generate_stream(buffer), media_type="image/png")


EXAMPLE_GATE_LIST = Body(
    examples=[GateList(gates=[HGate(qubit=0), CxGate(control_qubit=0, target_qubit=1)])]
)


@circuit_router.post(
    "/code",
    summary="Generate code for building a quantum circuit",
    description="Given a list of gates, the code for building the circuit will be generated.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"model": GeneratedCode, "description": "The generated code"},
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _generate_code(dto: GateList = EXAMPLE_GATE_LIST) -> GeneratedCode:
    graph = gates_converter.to_graph(dto.gates)
    build_steps = qiskit_generator.generate(graph)
    return GeneratedCode(code=build_steps)


@circuit_router.post(
    "/metrics",
    summary="Calculate metrics for a quantum circuit",
    description="Given a list of gates, the circuit will be analyzed and a set of metrics will be returned.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"model": MetricsResult, "description": "The calculated metrics"},
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _calculate_metrics(dto: GateList = EXAMPLE_GATE_LIST) -> MetricsResult:
    graph = gates_converter.to_graph(dto.gates)
    metrics = analyzer.calculate_metrics(graph)
    return MetricsResult(metrics=metrics)


EXAMPLE_GATES_TO_COMPARE = Body(
    examples=[
        GatesToCompare(
            old_gates=[HGate(qubit=0), XGate(qubit=0), HGate(qubit=0)],
            new_gates=[ZGate(qubit=0)],
        )
    ]
)


@circuit_router.post(
    "/compare",
    summary="Calculate the difference in metrics between two quantum circuits",
    description="Given two lists of gates, the difference of metrics between the new and the old circuits will be calculated.",
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.OK: {"model": DeltaMetricsResult, "description": "The difference in metrics"},
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "model": ErrorList | GateListErrors,
            "description": "Invalid input data",
        },
    },
)
def _compare_metrics(dto: GatesToCompare = EXAMPLE_GATES_TO_COMPARE) -> DeltaMetricsResult:
    old = gates_converter.to_graph(dto.old_gates)
    new = gates_converter.to_graph(dto.new_gates)
    delta_metrics = analyzer.compare_metrics(old, new)
    return DeltaMetricsResult(delta_metrics=delta_metrics)
