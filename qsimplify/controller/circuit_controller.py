"""A controller for the /api/circuit endpoint."""

from http import HTTPStatus

import fastapi
from fastapi import APIRouter

from qsimplify.analyzer import analyzer
from qsimplify.controller.dto import (
    DeltaMetricsResult,
    GateList,
    GatesToCompare,
    GeneratedCode,
    MetricsResult,
    SimplifiedCircuit,
)
from qsimplify.converter import GatesConverter, QiskitConverter
from qsimplify.drawer import Drawer
from qsimplify.generator import QiskitGenerator
from qsimplify.simplifier import Simplifier

circuit_router = APIRouter(prefix="/api/circuit")
gates_converter = GatesConverter()
qiskit_converter = QiskitConverter()
simplifier = Simplifier()
drawer = Drawer()
qiskit_generator = QiskitGenerator()


@circuit_router.post("/simplify", status_code=HTTPStatus.OK)
def _test(dto: GateList) -> SimplifiedCircuit:
    graph = gates_converter.to_graph(dto.gates)
    simplified_graph = simplifier.simplify_graph(graph)
    simplified_gates = [gate.model_dump() for gate in gates_converter.from_graph(simplified_graph)]
    original_metrics = analyzer.calculate_metrics(graph)
    new_metrics = analyzer.calculate_metrics(simplified_graph)
    delta_metrics = analyzer.compare_metrics(graph, simplified_graph)
    build_steps = qiskit_generator.generate(graph)

    return SimplifiedCircuit(
        simplified_gates, original_metrics, new_metrics, delta_metrics, build_steps
    )


@circuit_router.post("/plot", status_code=HTTPStatus.OK)
def _plot_circuit(dto: GateList) -> fastapi.Response:
    graph = gates_converter.to_graph(dto.gates)
    qiskit_circuit = qiskit_converter.from_graph(graph)
    buffer = drawer.save_circuit_to_buffer(qiskit_circuit)
    return fastapi.Response(content=buffer.getvalue(), media_type="image/png")


@circuit_router.post("/plot_graph", status_code=HTTPStatus.OK)
def _plot_graph(dto: GateList) -> fastapi.Response:
    graph = gates_converter.to_graph(dto.gates)
    buffer = drawer.save_graph_to_buffer(graph, "png", dpi=str(100))
    return fastapi.Response(content=buffer.getvalue(), media_type="image/png")


@circuit_router.post("/code", status_code=HTTPStatus.OK)
def _generate_code(dto: GateList) -> GeneratedCode:
    graph = gates_converter.to_graph(dto.gates)
    build_steps = qiskit_generator.generate(graph)
    return GeneratedCode(build_steps)


@circuit_router.post("/metrics", status_code=HTTPStatus.OK)
def _calculate_metrics(dto: GateList) -> MetricsResult:
    graph = gates_converter.to_graph(dto.gates)
    metrics = analyzer.calculate_metrics(graph)
    return MetricsResult(metrics)


@circuit_router.post("/compare", status_code=HTTPStatus.OK)
def _compare_metrics(dto: GatesToCompare) -> DeltaMetricsResult:
    old = gates_converter.to_graph(dto.old_gates)
    new = gates_converter.to_graph(dto.new_gates)
    delta_metrics = analyzer.compare_metrics(old, new)
    return DeltaMetricsResult(delta_metrics)
