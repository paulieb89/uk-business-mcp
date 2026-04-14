# uk-business-mcp (Ledgerhall proxy)

FastMCP proxy that bundles `govuk-mcp`, `uk-legal-mcp`, `uk-due-diligence-mcp`,
and `property-shared` behind a single URL. Marketed as the **Ledgerhall**
product on bouch.dev.

- **GitHub:** `paulieb89/uk-business-mcp`
- **Deployed:** `https://uk-business-mcp.fly.dev/mcp`
- **Shape:** non-standard — single `server.py` at repo root, no package. `uv sync` needs `--no-install-project`.

This repo has no domain tools of its own — it only proxies upstreams via
`create_proxy()`. All tool logic lives in the upstream servers.

## Not to be confused with

**`uk-due-diligence-mcp`** is a DIFFERENT repo at `/home/bch/dev/uk-due-diligence-mcp`,
deployed at `https://uk-due-diligence-mcp.fly.dev/mcp`. That repo is the
standalone Companies House / Charity / HMLR / Gazette / VAT server with 11 tools.
It is one of the upstreams this proxy mounts, not the same thing as this proxy.

The due-diligence folder was previously misleadingly named
`/home/bch/dev/uk-business-mcp` until 2026-04-14, which was the source of
repeated cross-repo confusion.
