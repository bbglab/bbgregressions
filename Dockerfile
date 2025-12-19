# Use the uv image with Python 3.13
FROM ghcr.io/astral-sh/uv:0.5-python3.13-bookworm-slim

# Set environment variables
ENV UV_COMPILE_BYTECODE=1

# Set the working directory to /bbgregressions
WORKDIR /bbgregressions

# Stage necessary files into the container
COPY uv.lock /bbgregressions/uv.lock
COPY pyproject.toml /bbgregressions/pyproject.toml
COPY src /bbgregressions/src
COPY LICENSE /bbgregressions/LICENSE
COPY README.md /bbgregressions/README.md

# Install dependencies and build the project
RUN mkdir -p /root/.cache/uv \
    && cd /bbgregressions \
    && uv sync --frozen --no-dev \
    && uv build \
    && pip install dist/*.tar.gz \
    # Clean up unnecessary files
    && rm -rf /root/.cache/uv /bbgregressions/build /bbgregressions/.venv

ENTRYPOINT ["bbgregressions"]