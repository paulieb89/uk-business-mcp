FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir hatchling

COPY pyproject.toml README.md ./
COPY server.py ./
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uk-business-mcp"]
