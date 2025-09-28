"""Contains part 1 of the QFT example usage, where both the original and simplified circuits can be sent to IBM's cloud."""

import os

import numpy
from loguru import logger
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.circuit.library import QFTGate
from qiskit.quantum_info import Operator
from qiskit_aer.primitives import SamplerV2 as Sampler
from qiskit_ibm_runtime import QiskitRuntimeService

from qsimplify import logging_config
from qsimplify.converter.qiskit_converter import QiskitConverter
from qsimplify.simplifier import Simplifier

_SEND_TO_IBM_CLOUD = True
logging_config.set_up_logging()

circuit = QuantumCircuit(3)

# Initial state
circuit.h(range(3))
circuit.p(numpy.pi / 2, 0)
circuit.p(numpy.pi / 4, 1)
circuit.p(numpy.pi / 2, 2)

# QFT
qft_circuit = QuantumCircuit(3)
qft_circuit.append(QFTGate(3), range(3))
circuit.compose(qft_circuit.decompose(), qubits=range(3), inplace=True)

circuit.draw("mpl").savefig("original.png")
logger.info(f"QFT3 circuit:\n{circuit.draw()}")
logger.info("QFT3 gates:", circuit.count_ops())
logger.info("QFT3 depth:", circuit.depth())

polluted = QuantumCircuit(3)

# Initial state
polluted.h(range(3))
polluted.p(numpy.pi / 2, 0)
polluted.p(numpy.pi / 4, 1)
polluted.p(numpy.pi / 2, 2)

# Polluted QFT
polluted.cz(0, 1)
polluted.h(2)
polluted.z(0)
polluted.cz(0, 1)
polluted.z(0)
polluted.cp(numpy.pi / 2, 1, 2)
polluted.h(1)
polluted.y(2)
polluted.y(2)
polluted.cp(numpy.pi / 4, 0, 2)
polluted.cp(numpy.pi / 2, 0, 1)
polluted.h(0)
polluted.cx(0, 2)
polluted.cx(2, 0)
polluted.cx(0, 2)

polluted.draw("mpl").savefig("polluted.png")
logger.info(f"Polluted circuit:\n{polluted.draw()}")
logger.info("Polluted gates:", polluted.count_ops())
logger.info("Polluted depth:", polluted.depth())

simplifier = Simplifier()
converter = QiskitConverter()

graph = converter.to_graph(polluted)
simplified_graph = simplifier.simplify_graph(graph, iterations=2)
simplified = converter.from_graph(simplified_graph)

simplified.draw("mpl").savefig("simplified.png")
logger.info(f"Simplified circuit:\n{simplified.draw()}")
logger.info("Simplified gates:", simplified.count_ops())
logger.info("Simplified depth:", simplified.depth())

logger.info("Is it the same as QFT(3)?", Operator(circuit).equiv(Operator(simplified)))

if not _SEND_TO_IBM_CLOUD:
    raise AssertionError("Exiting because SEND_TO_IBM_CLOUD is False")

_IBM_API_KEY = os.getenv("IBM_API_KEY", None)


class _QftError(Exception):
    pass


if _IBM_API_KEY is None:
    raise _QftError("Please set the IBM_API_KEY environment variable")

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    instance="qsimplify",
    token=_IBM_API_KEY,
    set_as_default=True,
    overwrite=True,
)
service = QiskitRuntimeService()

# Backend configuration
backend = service.backend(name="ibm_brisbane")
pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
sampler = Sampler()
SHOTS = 1024
sampler.options.default_shots = SHOTS

# Add measurements
polluted.measure_all()
simplified.measure_all()

# Job scheduling
polluted_job = sampler.run([pass_manager.run(polluted)])
logger.info(f"Polluted circuit ({SHOTS} shots) job ID is {polluted_job.job_id()}")
simplified_job = sampler.run([pass_manager.run(simplified)])
logger.info(f"Simplified circuit ({SHOTS} shots) job ID is {simplified_job.job_id()}")
