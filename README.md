# Quantum Circuit Simplifier

## Project dependencies

### Required

- uv is used to manage dependencies. You can check installation instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

### Optional

- Graphviz is used to draw graphs. You can check installation instructions [here](https://graphviz.org/download/).

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

- Run demo in debug mode (doesn't start a server)

```shell
uv run python -m qsimplify.demo --debug
```

- Start as a Flask server

```shell
uv run python -m qsimplify.app
```

- Start as a Flask server in debug mode

```shell
uv run python -m qsimplify.app --debug
```

- Build the demo Docker image

```shell
sudo docker rmi qsimplify_demo
sudo docker build -t qsimplify_demo -f Dockerfile.demo .
```

- Run the demo Docker image and keep the output files in the "out" subdirectory

```shell
mkdir out
sudo docker run -it --rm -v "$(pwd)/out:/app/out" qsimplify_demo
```

- Build the Flask server Docker image

```shell
sudo docker rmi qsimplify
sudo docker build -t qsimplify .
```

- Run the Flask server Docker image and expose it in port 5000

```shell
sudo docker run -it --rm -p 5000:5000 qsimplify
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
