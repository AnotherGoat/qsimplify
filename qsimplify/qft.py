import os

import numpy
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Operator
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_ibm_runtime import SamplerV2 as Sampler

from qsimplify.converter.qiskit_converter import QiskitConverter
from qsimplify.simplifier import Simplifier

circuit = QuantumCircuit(3)

# Initial state
circuit.h(range(3))
circuit.p(numpy.pi / 2, 0)
circuit.p(numpy.pi / 4, 1)
circuit.p(numpy.pi / 2, 2)

# QFT
circuit.compose(QFT(3).decompose(), qubits=range(3), inplace=True)

circuit.draw("mpl").savefig("original.png")
print(circuit.draw())
print("QFT3 gates:", circuit.count_ops())
print("QFT3 depth:", circuit.depth())

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
print(polluted.draw())
print("Polluted gates:", polluted.count_ops())
print("Polluted depth:", polluted.depth())

simplifier = Simplifier()
converter = QiskitConverter()

graph = converter.to_graph(polluted)
simplified_graph = simplifier.simplify_graph(graph, iterations=2)
simplified = converter.from_graph(simplified_graph)

simplified.draw("mpl").savefig("simplified.png")
print(simplified.draw())
print("Simplified gates:", simplified.count_ops())
print("Simplified depth:", simplified.depth())

print("Is it the same as QFT(3)?", Operator(circuit).equiv(Operator(simplified)))

load_dotenv()

IBM_API_KEY = os.getenv("IBM_API_KEY", None)

assert False

if IBM_API_KEY is None:
    raise Exception("Please set the IBM_API_KEY environment variable")

QiskitRuntimeService.save_account(
    channel="ibm_quantum", token=IBM_API_KEY, set_as_default=True, overwrite=True
)
service = QiskitRuntimeService()

# Backend configuration
backend = service.backend(name="ibm_brisbane")
pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
sampler = Sampler(mode=backend)
SHOTS = 131072
sampler.options.default_shots = SHOTS

# Add measurements
polluted.measure_all()
simplified.measure_all()

# Job scheduling
polluted_job = sampler.run([pass_manager.run(polluted)])
print(f"Polluted circuit ({SHOTS} shots) job ID is {polluted_job.job_id()}")
simplified_job = sampler.run([pass_manager.run(simplified)])
print(f"Simplified circuit ({SHOTS} shots) job ID is {simplified_job.job_id()}")
