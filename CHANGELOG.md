# Changelog

All notable changes to `uk-business-mcp` (Ledgerhall) are documented here, starting with 0.4.0. Earlier releases are described in their GitHub release notes.

## [0.4.1] — 2026-11-18

### Fixed

- `GET /mcp` returns 405 instead of a held-open empty event stream, matching the upstream servers (#12).
- `/health` lists the upstreams from the first request after boot; it was empty for the first minute (#13).

## [0.4.0] — 2026-11-18

### Changed

- FastMCP 3.2.4 → 4.1.8 and MCP SDK 1.27.0 → 2.3.0, the same SDK line as the upstreams. No change to the proxied tool surface.

### Added

- `/health` reports `version`, `git_sha`, and each upstream's `status`, `version` and `git_sha` (cached for 60 s; an upstream outage does not change the proxy's own `status`).
- `docs/tool-reference.md`, generated from `fastmcp inspect`.
