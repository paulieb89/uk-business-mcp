# AGENTS.md — uk-business-mcp (Ledgerhall)

AI agent instructions for working in this repo. See `/home/bch/dev/ops/OPS.md` for credentials, fleet overview, and release tooling.

## Repo shape

Single `server.py`. FastMCP proxy aggregating four upstream MCP servers under one endpoint.
No domain tools of its own — all requests forwarded via `create_proxy()` + `mount()`.
GitHub repo: `paulieb89/uk-business-mcp`
Disk path: `/home/bch/dev/mcpfleet/uk-business-mcp/`
(`00_RELEASE/uk-business-mcp` is a stale pre-observability snapshot — do not work there.)

## Upstreams

| Prefix | Server | URL |
|--------|--------|-----|
| `gov_` | govuk-mcp | https://govuk-mcp.fly.dev/mcp |
| `law_` | uk-legal-mcp | https://uk-legal-mcp.fly.dev/mcp |
| `dd_` | uk-due-diligence-mcp | https://uk-due-diligence-mcp.fly.dev/mcp |
| `prop_` | property-shared | https://property-shared.fly.dev/mcp |

## Deploy

Releases are **GitHub-release-triggered** like the rest of the fleet:
`release.yml` runs `on: release: published` → PyPI (trusted publisher, `pypi`
environment) → `flyctl deploy`. A hand `fly deploy` ships prod but skips PyPI.

Single instance, lhr region. App name: `uk-business-mcp`.
Port: `server.py` reads `PORT` (default 8080); fly.toml `internal_port = 8080`.

## Version bump

1. Update `version` in `pyproject.toml`
2. Update version string in the `smithery_server_card` route in `server.py`
3. Commit, tag `vX.Y.Z`, push + push tag
4. `gh release create` — the workflow publishes to PyPI then deploys

Published on PyPI as `uk-business-mcp` (0.1.1+).

## Standard routes (must always be present)

- `/.well-known/mcp/server-card.json` — Smithery metadata
- `/.well-known/glama.json` — Glama maintainer claim
- `/health` — Fly health check

Verify after deploy:
```bash
curl https://uk-business-mcp.fly.dev/.well-known/mcp/server-card.json
curl https://uk-business-mcp.fly.dev/.well-known/glama.json
curl https://uk-business-mcp.fly.dev/health
```

## Do not

- Do not add domain tools — this is a pure proxy
- Do not use `FASTMCP_PORT` — the server reads `PORT` (default 8080)
- Do not commit API keys — no secrets required
