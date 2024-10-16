# Quantum Circuit Simplifier

## Running the program

Install dependencies

```shell
poetry install
```

Run unit tests

```shell
poetry run pytest
```

Run demo

```shell
poetry run python -m quantum_circuit_simplifier
```

Run demo in debug mode

```shell
poetry run python -m quantum_circuit_simplifier --debug
```

## Supported gates

- id
- h
- x
- y
- z
- swap
- ch
- cx
- cz
- cswap
- ccx
