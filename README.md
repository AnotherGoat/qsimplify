# QSimplify

A quantum circuit simplifier prototype, available as a FastAPI REST API.

## Example usage

https://github.com/user-attachments/assets/9f7d0529-8752-43ca-ac05-570e79179afe

## Simplification rules

[A catalogue of equivalent quantum circuits](docs/quantum_circuit_equivalences.pdf) is included as an extra document, which contains every simplification rule used by the program by default. The code parses the catalogue from [a JSON file](qsimplify/simplifier/default_rules.json).

## Project dependencies

If you are not using Docker to run the project, you may have to install the following dependencies:

### Required

- `uv` is used for dependency management. [Intallation instructions](https://docs.astral.sh/uv/getting-started/installation/).

### Optional

- `Graphviz` is used for drawing quantum circuit graphs. [Intallation instructions](https://graphviz.org/download/).

## Running the program

- Install pre-commit hooks (run once after pulling the repository)

```shell
uv run pre-commit install
```

- Install dependencies

```shell
uv sync
```

- Run unit tests

```shell
uv run pytest
```

- Run unit tests with coverage

```shell
uv run pytest --cov=qsimplify --cov-report=html:coverage
```

- Lint code

```shell
uv run ruff check qsimplify/
```

- Format code

```shell
uv run ruff check --fix --select I && uv run ruff format
```

- Check types

```shell
uv run pyright
```

- Run demo (doesn't start a server)

```shell
uv run python -m qsimplify.demo
```

- Start as a FastAPI server

```shell
uv run python -m qsimplify.app
```

- Build the demo Docker image

```shell
docker rmi qsimplify_demo
docker build -t qsimplify_demo -f demo.Dockerfile .
```

- Run the demo Docker image and keep the output files in the "out" subdirectory

```shell
mkdir out
docker run -it --rm -v "$(pwd)/out:/app/out" qsimplify_demo
```

- Build the FastAPI server Docker image

```shell
docker rmi qsimplify
docker build -t qsimplify .
```

- Run the FastAPI server Docker image and expose it in port 5001

```shell
docker run -it --rm -p 5001:5001 qsimplify
```

- Create SonarQube container for analysis

```shell
docker volume create --name sonarqube_data
docker volume create --name sonarqube_logs
docker volume create --name sonarqube_extensions
docker run --name sonarqube -p 9000:9000 sonarqube
```

Then log in as admin on http://localhost:9000 and create a project with key and name "qsimplify"

- Analyze project with SonarQube (include your own generated token)

```shell
docker start -i sonarqube
uv run pytest --cov=qsimplify --cov-report=xml
uv run pysonar --sonar-host-url=http://localhost:9000 --sonar-token=TOKEN
```

## Examples

### Draw supported gates

```python
import numpy
from qiskit import QuantumCircuit
from qsimplify.converter import QiskitConverter
from qsimplify.drawer import Drawer

circuit = QuantumCircuit(3, 1)
circuit.h(0)
circuit.ch(1, 2)
circuit.x(0)
circuit.cx(1, 2)
circuit.y(0)
circuit.swap(1, 2)
circuit.z(0)
circuit.cz(1, 2)
circuit.ccx(0, 1, 2)
circuit.cswap(0, 1, 2)
circuit.rx(numpy.pi, 0)
circuit.ry(numpy.pi / 2, 1)
circuit.rz(numpy.pi / 4, 2)
circuit.measure(0, 0)

converter = QiskitConverter()
graph = converter.circuit_to_graph(circuit)

drawer = Drawer(view=True)
drawer.save_circuit_png(circuit, "circuit")
drawer.save_graph_png(graph, "graph")
```
