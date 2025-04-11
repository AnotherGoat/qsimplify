# Quantum Circuit Simplifier

## Project dependencies

### Required

- Poetry is used to manage dependencies. You can check installation instructions [here](https://python-poetry.org/docs/#installation).

### Optional

- Graphviz is used to draw graphs. You can check installation instructions [here](https://graphviz.org/download/).

## Running the program

- Install dependencies

```shell
uv sync
```

- Run unit tests

```shell
uv run --group=test pytest
```

- Run unit tests with coverage

```shell
uv run --group=test pytest --cov=qsimplify --cov-report=html:coverage
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

- Run demo

```shell
uv run python -m qsimplify
```

- Run demo in debug mode

```shell
uv run python -m qsimplify --debug
```

- Build the Docker image

```shell
sudo docker build -t qsimplify .
```

- Run the Docker image and keep the output files in the "out" subdirectory

```shell
mkdir out
sudo docker run -it --rm -v "$(pwd)/out:/app/out" qsimplify
```

## Examples

### Draw supported gates

```python
import numpy
from qiskit import QuantumCircuit
from qsimplify.converter import Converter
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

converter = Converter()
graph = converter.circuit_to_graph(circuit)

drawer = Drawer(view=True)
drawer.save_circuit_png(circuit, "circuit")
drawer.save_graph_png(graph, "graph")
```
