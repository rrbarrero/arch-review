FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /workspace

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY app ./app

EXPOSE 8000

CMD ["uv", "run", "--frozen", "fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
