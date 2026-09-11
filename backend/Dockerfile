FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.5

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --group dev

COPY . .
EXPOSE 8000
CMD ["sh", "-c", "uv sync --frozen --group dev && alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
