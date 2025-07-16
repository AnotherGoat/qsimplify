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

# Install Graphviz (used for drawing graphs)
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends -y graphviz && \
    apt-get clean

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.7.17 /uv /uvx /bin/

# Copy project files
WORKDIR /app
COPY . ./

# Set ownership for all the copied files and install project dependencies
RUN chown -R appuser:appgroup /app && \
    uv sync --frozen

# Set app user
USER appuser

CMD ["uv", "run", "python", "-m", "qsimplify.demo"]
ENTRYPOINT ["uv", "run"]
