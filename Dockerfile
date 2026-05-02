FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8080

CMD ["uv", "run", "--no-dev", "streamlit", "run", "app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8080", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
