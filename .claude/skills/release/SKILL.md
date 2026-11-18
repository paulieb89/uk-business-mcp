---
name: release
description: Cut and ship a uk-business-mcp (Ledgerhall proxy) release. Use when asked to release, cut a release, ship, or deploy this project.
disable-model-invocation: true
---

The procedure around `.github/workflows/release.yml` (tool-reference check →
build → PyPI → `flyctl deploy` with the `GIT_SHA` build arg). Read it rather
than trusting a paraphrase. Don't run `fly deploy` by hand except for a
rollback the user has asked for.

This repo is a pure proxy over four live upstreams (`gov_`, `law_`, `dd_`,
`prop_`), so its own releases are mostly dependency bumps and proxy plumbing,
and an upstream release reaches Ledgerhall clients without one.

## Gates (shared with uk-legal-mcp and uk-due-diligence-mcp)

- **One approval gate: `gh release create`.** PRs may be merged once the local
  checks pass — there is no PR CI: `uv run --no-sync pytest -q` and
  `uv run --no-sync python scripts/gen_reference.py --check`.
- **One repo at a time.** Release, verify prod, then the next repo. If any prod
  check fails, stop and give the rollback.
- **Proxy live checks before and after.** There is no staging app; "before" is
  the current prod proxy plus a local run of the merged `main` (step 7).
- **State the rollback before asking for the gate** (see Rollback below).
- CHANGELOG names breaking changes tersely; check every line against the code.

## Steps

1. Verify `main` is clean and up to date with `origin/main`.
2. Baseline: `uv run --no-sync python tests/live/upstream_audit_via_proxy.py dd`
   and `... law` against prod (default URL). Both must pass before you change
   anything, or you can't tell what the release broke.
3. Branch, make the change, run the local checks.
4. Bump `version` in `pyproject.toml` and the `smithery_server_card` string in
   `server.py`; `uv lock`; add a `CHANGELOG.md` entry.
5. Open the PR(s) and merge once the local checks pass.
6. Pull `main`.
7. Run `main` locally against the real upstreams and repeat step 2 against it:
   `PORT=18090 uv run --no-sync python server.py &` then
   `... upstream_audit_via_proxy.py dd --url http://localhost:18090/mcp` (and
   `law`). Check `curl localhost:18090/health` lists all four upstreams.
8. Tag the merge commit `vX.Y.Z`, push the tag separately. State the rollback,
   then ask for the gate. On approval, `gh release create vX.Y.Z --verify-tag`
   and watch `release.yml` with `gh run watch --exit-status`.
9. Verify prod:
   - `/health` shows the version, the tag's SHA, and each upstream's
     version/git_sha (govuk-mcp and property-shared may report none);
   - the proxy live checks for `dd` and `law` against prod;
   - the upstreams still attribute the proxy's connections to `ledgerhall`
     (`sum by (client_name) (uk_legal_client_connections_total)` and the
     `uk_due_diligence_` equivalent via Fly Prometheus, `Authorization: FlyV1
     <fly auth token>`), with no new `mcp` default-name bucket.

## Rollback

State all three before asking for the gate:

- Previous image: `fly releases -a uk-business-mcp --image` (the current top
  row is what a rollback restores).
- Command: `fly deploy -a uk-business-mcp --image <previous image>`.
- PyPI: yanking is web-only —
  `https://pypi.org/manage/project/uk-business-mcp/release/X.Y.Z/` → Yank.
