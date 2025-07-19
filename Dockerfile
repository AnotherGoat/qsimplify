# Minified Python container
FROM python:3.12-slim

ARG UID=1000
ARG GID=1000

# Create non-root user and install Graphviz (used for drawing graphs)
RUN addgroup --gid "$GID" appgroup && \
    adduser --uid "$UID" --gid "$GID" --disabled-password --gecos "" appuser && \
    apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends -y graphviz && \
    apt-get clean

# Send output streams straight into the terminal, without buffering them
ENV PYTHONUNBUFFERED=1

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

# Copy project files
WORKDIR /app
COPY .python-version pyproject.toml uv.lock ./
COPY qsimplify ./qsimplify/

# Set ownership for all the copied files
RUN uv sync --no-dev --frozen && \
    chown -R appuser:appgroup /app

# Set app-specific environment variables
ENV LOG_LEVEL=INFO
ENV LOG_TO_FILE=False
ENV API_HOST=0.0.0.0
ENV API_PORT=5001
ENV API_RELOAD=False

# Set app user
USER appuser

CMD ["uv", "run", "--no-dev", "python", "-m", "qsimplify.app"]
