"""P3 regression test: tool-call metrics on the proxy topology.

uk-business-mcp is a pure proxy — every real tool call passes through
`create_proxy(Client(<upstream>))` mounted under a namespace (gov/law/dd/prop).
This is exactly the topology probes/fastmcp-error-shapes/PROBE-REPORT.md's P3
finding is about: on the fleet's locked fastmcp==3.2.4, a structured ToolError
raised by the backend arrives at the gateway's middleware as an EXCEPTION; on
fastmcp 3.4.x the same failure arrives as a *result* with is_error=True and no
exception at all. mcpfleet_obs.FleetMetricsMiddleware counts both paths — this
test pins that dual-path behaviour against this repo's own proxy-mounting code
so a future fastmcp version bump can't silently stop counting proxied errors.

Deliberately does NOT import server.py: the real module mounts create_proxy()
against four live *.fly.dev upstreams at import time, which would make this
test suite perform live network calls (and fail offline / in CI). Instead this
recreates server.py's exact mounting pattern in-process against a local stub
FastMCP backend, so the proxy hop is real but nothing leaves the machine.
"""

from prometheus_client import CollectorRegistry
from fastmcp import Client, FastMCP
from fastmcp.server import create_proxy

from mcpfleet_obs import install, parse_error_payload, raise_tool_error


def _build_stub_backend() -> FastMCP:
    stub = FastMCP(name="stub")

    @stub.tool()
    def stub_fail() -> str:
        raise_tool_error(
            "transient",
            is_retryable=True,
            attempted="stub_fail()",
            description="d",
        )

    @stub.tool()
    def stub_ok() -> str:
        return "fine"

    return stub


def _build_gateway(registry: CollectorRegistry) -> FastMCP:
    gw = FastMCP(name="gw")
    install(gw, prefix="uk_business", registry=registry)
    # Mirrors server.py's `mcp.mount(create_proxy(_upstream(url)), namespace=...)` —
    # only the client target (a local stub, not a live fly.dev URL) differs.
    gw.mount(create_proxy(Client(_build_stub_backend())), namespace="dd")
    return gw


async def test_proxied_tool_error_counts_as_error_with_category():
    registry = CollectorRegistry()
    gw = _build_gateway(registry)

    async with Client(gw) as client:
        tool_names = [t.name for t in await client.list_tools()]
        assert "dd_stub_fail" in tool_names

        raw = await client.call_tool_mcp("dd_stub_fail", {})

    assert raw.isError is True
    payload = parse_error_payload(raw.content[0].text)
    assert payload is not None
    assert payload.error_category == "transient"
    assert payload.is_retryable is True

    value = registry.get_sample_value(
        "uk_business_tool_calls_total",
        {
            "tool": "dd_stub_fail",
            "transport": "http",
            "region": "local",
            "status": "error",
            "error_category": "transient",
        },
    )
    assert value == 1.0


async def test_proxied_tool_success_counts_as_ok():
    registry = CollectorRegistry()
    gw = _build_gateway(registry)

    async with Client(gw) as client:
        tool_names = [t.name for t in await client.list_tools()]
        assert "dd_stub_ok" in tool_names

        raw = await client.call_tool_mcp("dd_stub_ok", {})

    assert not raw.isError

    value = registry.get_sample_value(
        "uk_business_tool_calls_total",
        {
            "tool": "dd_stub_ok",
            "transport": "http",
            "region": "local",
            "status": "ok",
            "error_category": "",
        },
    )
    assert value == 1.0
