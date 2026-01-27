FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY entrypoint.sh pyproject.toml uv.lock /app/

RUN uv sync --frozen --dev

COPY . /app/

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
