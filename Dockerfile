FROM python:3.12-slim

WORKDIR /app

# Keep in sync with pyproject.toml [project.dependencies]
# mcpfleet-obs must be published on PyPI (Gate 1) before this image can build;
# it pulls in prometheus-client (>=0.20) transitively, which is why that
# package is not pinned separately here.
COPY server.py ./
RUN pip install --no-cache-dir \
    "fastmcp==3.2.4" \
    "mcp==1.27.0" \
    "pydantic==2.13.0" \
    "httpx==0.28.1" \
    "uvicorn==0.44.0" \
    "zstandard>=0.22.0" \
    "brotli>=1.1.0" \
    "mcpfleet-obs==0.1.0"

EXPOSE 8000

CMD ["python", "server.py"]
