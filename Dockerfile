FROM python:3.12-slim

WORKDIR /app

COPY server.py ./
RUN pip install --no-cache-dir "fastmcp==3.2.4" "uvicorn>=0.30.0" "zstandard>=0.22.0"

EXPOSE 8000

CMD ["python", "server.py"]
