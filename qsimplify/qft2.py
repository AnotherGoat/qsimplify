import csv
import os
from dataclasses import dataclass
from pathlib import Path

import numpy
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv()

IBM_API_KEY = os.getenv("IBM_API_KEY", None)

if IBM_API_KEY is None:
    raise Exception("Please set the IBM_API_KEY environment variable")


@dataclass
class Result:
    circuit_name: str
    backend: str
    shots: int
    counts: dict[str, int]

    @property
    def percentages(self) -> dict[str, float]:
        total = sum(self.counts.values())
        return {bits: count / total for bits, count in self.counts.items()}

    def total_variation_distance(self, expected_counts: dict[str, int]) -> float:
        actual_total = sum(self.counts.values())
        expected_total = sum(expected_counts.values())

        joined_keys = set(self.counts.keys()) | set(expected_counts.keys())
        error = 0

        for key in joined_keys:
            actual_probability = self.counts.get(key, 0) / actual_total
            expected_probability = expected_counts.get(key, 0) / expected_total
            error += abs(actual_probability - expected_probability)

        return error / 2


results: list[Result] = []

# Circuit for running the simulation
circuit = QuantumCircuit(3)

# Initial state
circuit.h(range(3))
circuit.p(numpy.pi / 2, 0)
circuit.p(numpy.pi / 4, 1)
circuit.p(numpy.pi / 2, 2)

# QFT
circuit.compose(QFT(3).decompose(), qubits=range(3), inplace=True)

# Measurement
circuit.measure_all()

simulator = AerSimulator()
transpiled_circuit = transpile(circuit, simulator)
simulated_result = simulator.run(transpiled_circuit, shots=16384).result()
counts = simulated_result.get_counts()

results.append(Result("Simplified", "aer_simulator", 16384, counts))

QiskitRuntimeService.save_account(
    channel="ibm_quantum", token=IBM_API_KEY, set_as_default=True, overwrite=True
)
service = QiskitRuntimeService()


@dataclass
class Job:
    id: str
    name: str
    shots: int


JOBS = [
    Job("d107w2rv3z5000827vj0", "Polluted", 1024),
    Job("d107w38n2txg008jdc70", "Simplified", 1024),
    Job("d109rw3mya70008e779g", "Polluted", 16384),
    Job("d109rwkmya70008e77a0", "Simplified", 16384),
    Job("d109t9hmya70008e77g0", "Polluted", 65536),
    Job("d109ta15z6q00086yyjg", "Simplified", 65536),
    Job("d10e8esqf56g0081dkng", "Polluted", 131072),
    Job("d10e8fhv3z5000829pw0", "Simplified", 131072),
]

for job in JOBS:
    ibm_job = service.job(job.id)
    result = ibm_job.result()
    counts = result[0].data.meas.get_counts()

    results.append(Result(job.name, "ibm_brisbane", job.shots, counts))


def format_percent(percent: float) -> str:
    return f"{percent * 100:.2f}%"


with Path("results.csv").open("w") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(
        [
            "circuit",
            "backend",
            "shots",
            "000",
            "001",
            "010",
            "011",
            "100",
            "101",
            "110",
            "111",
            "total_variation_distance",
        ]
    )
    expected_counts = results[0].counts

    for result in results:
        writer.writerow(
            [
                result.circuit_name,
                result.backend,
                result.shots,
                format_percent(result.percentages.get("000", 0)),
                format_percent(result.percentages.get("001", 0)),
                format_percent(result.percentages.get("010", 0)),
                format_percent(result.percentages.get("011", 0)),
                format_percent(result.percentages.get("100", 0)),
                format_percent(result.percentages.get("101", 0)),
                format_percent(result.percentages.get("110", 0)),
                format_percent(result.percentages.get("111", 0)),
                format_percent(result.total_variation_distance(expected_counts)),
            ]
        )
