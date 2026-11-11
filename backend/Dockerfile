# Stage 1: Build dependencies using uv
FROM python:3.14-slim AS builder

# Copy the official uv binary from Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy dependency files
COPY uv.lock pyproject.toml ./

# Create the virtual environment explicitly using the system python of this image
RUN uv venv /app/.venv

# Install dependencies into the virtual environment without building the project yet
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code and install the project itself
COPY . /app
RUN uv sync --frozen --no-dev

# Stage 2: Final runtime image (with uv included)
FROM python:3.14-slim

WORKDIR /app

# Copy the fully prepared virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy the uv binary into the final image
COPY --from=builder /bin/uv /bin/uv

# Copy the application source code
COPY . /app

# Place the virtual environment's binaries at the front of the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Point uv to a writable cache directory to prevent permission errors
ENV UV_CACHE_DIR=/tmp/uv-cache

EXPOSE 8000

CMD ["uvicorn", "src.documentation_digester.api.main:app", "--host", "0.0.0.0", "--reload"]