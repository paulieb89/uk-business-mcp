FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /bin/uv

# Dependencies come from uv.lock — the image installs exactly what the lock
# resolves, transitives included. The previous hand-maintained pip list carried
# a "keep in sync with pyproject.toml" comment and had already drifted: it
# pinned mcpfleet-obs==0.1.0 while pyproject floated >=0.1.0, so prod ran 0.1.0
# without the validation-labelling fix while every other install got 0.2.0.
# It also pinned only the 7 direct deps, leaving the rest of the resolution
# (prometheus-client, starlette, anyio, ...) free to move between builds of the
# same commit.
#
# --no-install-project keeps this layer cached when only application code
# changes; the app is not imported as a package — CMD runs server.py from /app.
#
# mcpfleet-obs must be published on PyPI (Gate 1) before this image can build.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY server.py ./

# Run out of the synced environment rather than the system interpreter.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "server.py"]
