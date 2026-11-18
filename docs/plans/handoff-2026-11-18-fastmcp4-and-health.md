---
status: landed
repo: uk-business-mcp
date: 2026-11-18
supersedes: none
sessions: one Claude Code session, 2026-11-18 (FastMCP 4 bump → 0.4.0 → 0.4.1)
---

# Handoff: FastMCP 4.1.8, stack view on /health, GET 405 (0.4.0, 0.4.1)

## Purpose and scope

Move the proxy to FastMCP 4, make `/health` show the whole stack, and drop the
held-open GET shim. Shape A of the fleet handoff template
([uk-due-diligence-mcp/docs/plans/TEMPLATE-handoff.md](https://github.com/paulieb89/uk-due-diligence-mcp/blob/main/docs/plans/TEMPLATE-handoff.md)).
Changes: [CHANGELOG](../../CHANGELOG.md). PRs: #10 and #11 (0.4.0), #15 and #16
(0.4.1), #9 (proxy live check), #14 (README).

## What shipped

- **0.4.0, `v0.4.0` → `880fd33`:**
  - fastmcp 3.2.4 → 4.1.8 and mcp 1.27.0 → 2.3.0. 4.1.8 is the latest 4.1.x, with
    4.1.5's mount fixes and 4.1.7's proxy-caching fixes.
  - `/health` reports `version`, `git_sha` and each upstream's
    status/version/git_sha.
  - A generated [tool reference](../tool-reference.md).
  - The `/release` skill.
- **0.4.1, `v0.4.1` → `25c7767`:**
  - `GET /mcp` returns 405 (`_HttpGuard` removed, #12).
  - `/health` lists the upstreams from boot (#13: the cache started at `at=0.0`,
    and `monotonic()` counts from boot).
- **Checks for both:**
  - prod `/health` version and SHA;
  - `tests/live/upstream_audit_via_proxy.py` dd 8/8 and law 11/11, before and
    after;
  - upstreams still label the proxy's connections `ledgerhall` (legal 193→320,
    DD 86→199; bare `mcp` flat);
  - 0.4.1's first `/health` after boot (VM up 30.7 s) lists all four upstreams;
  - `GET /mcp` returns 405.
- Rollback image for 0.4.1: Fly v26,
  `registry.fly.io/uk-business-mcp:deployment-01M7QX03SJ6T4T90WJ31RR5VJA` (0.4.0).

## Decisions

1. **`/health` never fails because of an upstream.** Upstream status is cached for
   60 s, with a 2.5 s timeout per upstream. Fly probes `/health` every 30 s with a
   5 s timeout, so an upstream outage must not get this machine restarted.
2. **Proxy checks run before and after, against prod and a local run of `main`.**
   This repo has no staging app.

## govuk-mcp's overload was not caused by this proxy

govuk sat at its 50-connection limit all day, while this proxy made 0–13 `gov_`
calls per half-hour. Clients (mostly Claude Code) holding govuk's own `GET /mcp`
streams were the cause; fixed in govuk-mcp 0.3.2. The same shim is still in
pinescript-mcp (#8 there) and whatdotheyknow-mcp (#6 there).

## Gotchas

- `time.monotonic()` is small on a freshly booted Fly VM. Never initialise a TTL
  timestamp to 0.
- With `_HttpGuard` present, a `TestClient` GET test hangs rather than failing.
- PyPI's `/pypi/<pkg>/json` can serve a stale cached copy right after publishing;
  `/pypi/<pkg>/<version>/json` confirms the new version.
- `fastmcp inspect` here lists the live upstreams' tools, so
  `gen_reference.py --check` drifts whenever an upstream changes its surface.
  Regenerate the reference when that happens.

## Open issues

#6 (Dockerfile `EXPOSE 8000`) · fleet tooling: [mcpfleet-obs #10](https://github.com/uk-agents/mcpfleet-obs/issues/10)

## Recommended next step

FastMCP 4.1.8 across the upstreams, so the fleet runs one patch
([DD #49](https://github.com/paulieb89/uk-due-diligence-mcp/issues/49),
[legal #116](https://github.com/paulieb89/uk-legal-mcp/issues/116),
[govuk #11](https://github.com/paulieb89/govuk-mcp/issues/11)). Re-run the proxy
checks after each one. Then the stdio entry points
([DD #51](https://github.com/paulieb89/uk-due-diligence-mcp/issues/51),
[govuk #8](https://github.com/paulieb89/govuk-mcp/issues/8)).

## Re-verify

```bash
curl -s https://uk-business-mcp.fly.dev/health
curl -sS -m 10 -o /dev/null -w '%{http_code}\n' -H 'Accept: text/event-stream' https://uk-business-mcp.fly.dev/mcp   # 405
uv run --no-sync python tests/live/upstream_audit_via_proxy.py dd
uv run --no-sync python tests/live/upstream_audit_via_proxy.py law
```
