FROM python:3.12-slim

WORKDIR /app

# Keep in sync with pyproject.toml [project.dependencies]
COPY server.py ./
RUN pip install --no-cache-dir \
    "fastmcp==3.2.4" \
    "mcp==1.27.0" \
    "pydantic==2.13.0" \
    "httpx==0.28.1" \
    "uvicorn==0.44.0" \
    "zstandard>=0.22.0"

EXPOSE 8000

CMD ["python", "server.py"]
