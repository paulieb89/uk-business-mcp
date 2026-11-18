import asyncio
import os
import time
import tomllib
from importlib.metadata import PackageNotFoundError, version as _pkg_version
from pathlib import Path

import httpx

from fastmcp import Client, FastMCP
from fastmcp.server import create_proxy
from mcp.types import Implementation
from mcpfleet_obs import install
from starlette.responses import JSONResponse

# Identify Ledgerhall to its own upstreams. Without this, every proxied connection
# handshakes as the SDK default `mcp/0.1.0` — and because stateless_http=True gives
# each request a fresh transport, that is one upstream initialize PER REQUEST. On
# uk-legal-mcp, whose ClientTrackingMiddleware is the only place in the fleet that
# records clientInfo, `mcp/0.1.0` is the largest bucket at 9,336 connections: our
# own facade, indistinguishable from strangers and outweighing every real client.
# The upstreams cannot attribute what we never tell them, so tell them.
_CLIENT_INFO = Implementation(name="ledgerhall", version="0.1.0")


def _upstream(url: str) -> Client:
    return Client(url, client_info=_CLIENT_INFO)

mcp = FastMCP(
    "UK Business",
    instructions=(
        "Ledgerhall: UK public data for AI agents. Four upstream namespaces:\n"
        "\n"
        "  gov_*   — GOV.UK: 700k+ pages, organisations, postcodes\n"
        "  law_*   — UK Legal: case law, legislation, Hansard, HMRC guidance, OSCOLA\n"
        "  dd_*    — Due Diligence: Companies House, Charity Commission, Land Registry, Gazette, sanctions\n"
        "  prop_*  — Property: Land Registry, EPC, Rightmove, yields, stamp duty, planning\n"
        "\n"
        "Due diligence workflow — search first, then fetch detail:\n"
        "  dd_company_search    → find a company, get company_number\n"
        "  dd_company_profile   → full CH profile (status, address, SIC, filing flags)\n"
        "  dd_company_officers  → active directors with nominee risk flag\n"
        "  dd_company_psc       → persons with significant control\n"
        "  dd_charity_search    → find a charity, get charity_number\n"
        "  dd_charity_profile   → full Charity Commission profile\n"
        "  dd_disqualified_search / dd_disqualified_profile → banned directors\n"
        "  dd_gazette_insolvency / dd_gazette_notice → insolvency notices\n"
        "  dd_land_title_search → HMLR title register"
    ),
)

# One declaration of the proxy mounts. mcpfleet-obs needs the same namespaces to
# label upstream failures source="upstream" rather than blaming this server, and
# a second hand-written copy of this list is a thing that drifts.
PROXY_MOUNTS = {
    "gov": "https://govuk-mcp.fly.dev/mcp",
    "law": "https://uk-legal-mcp.fly.dev/mcp",
    "dd": "https://uk-due-diligence-mcp.fly.dev/mcp",
    "prop": "https://property-shared.fly.dev/mcp",
}

for _namespace, _url in PROXY_MOUNTS.items():
    mcp.mount(create_proxy(_upstream(_url)), namespace=_namespace)


@mcp.custom_route("/.well-known/mcp/server-card.json", methods=["GET"])
async def smithery_server_card(request):
    return JSONResponse({"serverInfo": {"name": "uk-business-mcp", "version": "0.4.0"}})


@mcp.custom_route("/.well-known/glama.json", methods=["GET"])
async def glama_claim(request):
    return JSONResponse({
        "$schema": "https://glama.ai/mcp/schemas/connector.json",
        "maintainers": [{"email": "paul@bouch.dev"}],
    })


def _project_version() -> str:
    """Package version; the image does not install the project, so fall back
    to pyproject.toml (copied into the image) for the same number."""
    try:
        return _pkg_version("uk-business-mcp")
    except PackageNotFoundError:
        pyproject = Path(__file__).with_name("pyproject.toml")
        return tomllib.loads(pyproject.read_text())["project"]["version"]


SERVER_VERSION = _project_version()
# Commit the image was built from (Docker build arg from release.yml).
GIT_SHA = os.environ.get("GIT_SHA") or "unknown"

# /health also reports what each upstream mount is running, so one request shows
# the whole Ledgerhall stack (e.g. after an upstream release). Fly probes /health
# every 30s with a 5s timeout: the upstream view is cached for UPSTREAM_TTL and
# each upstream gets UPSTREAM_TIMEOUT, and an upstream being down never changes
# the proxy's own status — otherwise an upstream outage would restart this machine.
UPSTREAM_TTL = 60.0
UPSTREAM_TIMEOUT = 2.5
_upstream_cache: dict = {"at": 0.0, "data": {}}
_upstream_lock = asyncio.Lock()


async def _upstream_health(client: httpx.AsyncClient, url: str) -> dict:
    health_url = url.rsplit("/mcp", 1)[0] + "/health"
    try:
        resp = await client.get(health_url)
        body = resp.json() if resp.status_code == 200 else {}
        return {
            "status": body.get("status") or f"HTTP {resp.status_code}",
            "version": body.get("version"),
            "git_sha": body.get("git_sha"),
        }
    except (httpx.HTTPError, ValueError) as exc:
        return {"status": "unreachable", "error": type(exc).__name__}


async def _upstreams() -> dict:
    async with _upstream_lock:
        if time.monotonic() - _upstream_cache["at"] < UPSTREAM_TTL:
            return _upstream_cache["data"]
        async with httpx.AsyncClient(timeout=UPSTREAM_TIMEOUT) as client:
            results = await asyncio.gather(
                *(_upstream_health(client, url) for url in PROXY_MOUNTS.values())
            )
        _upstream_cache["data"] = dict(zip(PROXY_MOUNTS, results))
        _upstream_cache["at"] = time.monotonic()
        return _upstream_cache["data"]


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({
        "status": "ok",
        "version": SERVER_VERSION,
        "git_sha": GIT_SHA,
        "upstreams": await _upstreams(),
    })


# Fleet-standard observability: client tracking (who calls Ledgerhall — until this,
# the only server-side signal was upstream connections, e.g. 672 in ten hours to
# uk-due-diligence, 2.4x the next client, with nothing about who was calling
# Ledgerhall itself) + tool-call metrics (new: this proxy never had any) + /metrics.
# _AcceptNormalizer and _HttpGuard below only intercept /mcp, so /metrics passes
# through untouched — readable unauthenticated over HTTPS, which is what lets one
# sweep read every server's callers without a Fly token.
install(mcp, prefix="uk_business", proxy_namespaces=PROXY_MOUNTS)


class _HttpGuard:
    """Return a held-open SSE stream for GET /mcp; 405 for DELETE /mcp.

    claude.ai probes GET /mcp to establish an SSE stream before sending MCP
    protocol messages via POST. With stateless_http=True FastMCP only registers
    POST routes, so GET returns 405 — claude.ai treats this as a connection
    failure even though POST works fine.

    Fix: intercept GET /mcp and return 200 text/event-stream held open until
    the client disconnects. FastMCP never sees the GET; stateless semantics
    are preserved. DELETE is rejected (405) — stateless servers have no sessions.
    """

    def __init__(self, app, mcp_path: bytes = b"/mcp"):
        self.app = app
        self._mcp_path = mcp_path.rstrip(b"/")

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http":
            path = scope.get("path", "").rstrip("/").encode()
            method = scope.get("method", "").upper().encode()
            if path == self._mcp_path:
                if method == b"GET":
                    await send({"type": "http.response.start", "status": 200, "headers": [
                        (b"content-type", b"text/event-stream"),
                        (b"cache-control", b"no-cache"),
                        (b"connection", b"keep-alive"),
                    ]})
                    await send({"type": "http.response.body", "body": b"", "more_body": True})
                    while True:
                        event = await receive()
                        if event["type"] == "http.disconnect":
                            break
                    return
                if method == b"DELETE":
                    from starlette.responses import Response as StarletteResponse
                    await StarletteResponse("Method Not Allowed", status_code=405, headers={"Allow": "POST"})(scope, receive, send)
                    return
        await self.app(scope, receive, send)


class _AcceptNormalizer:
    """Stamp Accept to the MCP-spec value on /mcp only, so json_response=True never 406s.

    Anthropic sends mixed Accept headers per request type (application/json for
    initialize, text/event-stream for tools/list). Only stamp the MCP endpoint —
    leave /health and /.well-known/* with their original Accept headers.
    """
    def __init__(self, app, mcp_path: bytes = b"/mcp"):
        self.app = app
        self._mcp_path = mcp_path.rstrip(b"/")

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http" and scope.get("path", "").rstrip("/").encode() == self._mcp_path:
            headers = [
                (b"accept", b"application/json, text/event-stream")
                if name.lower() == b"accept"
                else (name, value)
                for name, value in scope.get("headers", [])
            ]
            scope = {**scope, "headers": headers}
        await self.app(scope, receive, send)


def main():
    import uvicorn
    from fastmcp.server.http import create_streamable_http_app

    # stateless_http=True: each request creates a fresh transport context.
    # Required for aggregator proxies (Lesson 32) and multi-machine Fly
    # deploys (Lesson 2) — without it, clients hit "Missing session ID"
    # on any request not preceded by initialize on the same machine.
    port = int(os.environ.get("PORT", "8080"))
    app = create_streamable_http_app(
        mcp,
        streamable_http_path="/mcp",
        json_response=True,
        stateless_http=True,
    )
    uvicorn.run(
        _HttpGuard(_AcceptNormalizer(app)),
        host="0.0.0.0",
        port=port,
        forwarded_allow_ips="*",
        proxy_headers=True,
        lifespan="on",
        log_level="info",
    )


if __name__ == "__main__":
    main()
