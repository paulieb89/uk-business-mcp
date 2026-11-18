"""Run an upstream server's validation-audit live script through this proxy.

uk-due-diligence-mcp and uk-legal-mcp each ship tests/live/validation_audit_calls.py,
which checks fixed behaviour against a deployed server. This runs the same calls
through uk-business-mcp, adding the mount prefix (dd_ / law_) to every tool name,
so a release of either upstream can be confirmed end to end through the proxy
(a live mount with no PyPI pin: it serves whatever the upstream has deployed).

Usage (from this repo; needs the sibling repos checked out next to it):
    uv run --no-sync python tests/live/upstream_audit_via_proxy.py dd
    uv run --no-sync python tests/live/upstream_audit_via_proxy.py law
    uv run --no-sync python tests/live/upstream_audit_via_proxy.py dd --url https://uk-business-mcp.fly.dev/mcp

The /health line printed is the proxy's own, which reports no version or git_sha;
check the upstream's /health for those. Exits 1 if any check fails. Not collected
by pytest (no test_ prefix): it needs live upstreams.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import sys
from pathlib import Path

FLEET = Path(__file__).resolve().parents[3]
SCRIPTS = {
    "dd": FLEET / "uk-due-diligence-mcp" / "tests" / "live" / "validation_audit_calls.py",
    "law": FLEET / "uk-legal-mcp" / "tests" / "live" / "validation_audit_calls.py",
}
DEFAULT_URL = "https://uk-business-mcp.fly.dev/mcp"


def _load(script: Path):
    if not script.exists():
        sys.exit(f"{script} not found — check out the upstream repo next to this one, or pass --script")
    spec = importlib.util.spec_from_file_location("upstream_audit_calls", script)
    module = importlib.util.module_from_spec(spec)
    # Registered before exec: the script's dataclasses resolve their module by name.
    sys.modules["upstream_audit_calls"] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prefix", choices=sorted(SCRIPTS), help="mount namespace of the upstream")
    parser.add_argument("--url", default=DEFAULT_URL, help="proxy MCP URL")
    parser.add_argument("--script", type=Path, help="override the upstream script path")
    args = parser.parse_args()

    module = _load(args.script or SCRIPTS[args.prefix])
    for call in module.CALLS:
        call.tool = f"{args.prefix}_{call.tool}"
    return asyncio.run(module.main(args.url))


if __name__ == "__main__":
    sys.exit(main())
