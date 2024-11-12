# Minified Python container
FROM python:3.11-slim

# Send output streams straight into the terminal, without buffering them
ENV PYTHONUNBUFFERED=1

# Install Graphviz (used for drawing graphs) and pipx (recommended way to use Poetry)
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends -y graphviz pipx

# Add root Python venv to path
ENV PATH="/root/.local/bin:${PATH}"

# Install Poetry
ENV POETRY_VERSION=1.8.3
RUN pipx install "poetry==$POETRY_VERSION"

# Create directory that output files are saved to
WORKDIR /app
RUN mkdir -p /app/out

# Install project dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-directory

COPY qsimplify/ ./qsimplify
COPY tests/ ./tests
RUN poetry install --only main

CMD ["poetry", "run", "python", "-m", "qsimplify"]
ENTRYPOINT ["poetry", "run"]
