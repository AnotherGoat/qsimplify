# Minified Python container
FROM python:3.12-slim

# Send output streams straight into the terminal, without buffering them
ENV PYTHONUNBUFFERED=1

# Install Graphviz (used for drawing graphs)
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends -y graphviz

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/

# Install project dependencies
WORKDIR /app
COPY . ./
RUN uv sync --frozen

# Set app environment variables
ENV DEBUG=False
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001
ENV FLASK_DEBUG=False

CMD ["uv", "run", "python", "-m", "qsimplify.app"]
ENTRYPOINT ["uv", "run"]
