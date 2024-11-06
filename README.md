# Quantum Circuit Simplifier

## Project dependencies

### Required

- Poetry is used to manage dependencies. You can check installation instructions [here](https://python-poetry.org/docs/#installation).

### Optional

- Graphviz is used to draw graphs. You can check installation instructions [here](https://graphviz.org/download/).

## Running the program

- Install dependencies

```shell
poetry install
```

- Run unit tests

```shell
poetry run pytest
```

- Run unit tests with coverage

```shell
poetry run pytest --cov=qsimplify --cov-report=html:coverage
```

- Lint code

```shell
poetry run pylint
```

- Format code

```shell
poetry run isort . && black .
```

- Check types

```shell
poetry run pyright
```

- Run demo

```shell
poetry run python -m qsimplify
```

- Run demo in debug mode

```shell
poetry run python -m qsimplify --debug
```
