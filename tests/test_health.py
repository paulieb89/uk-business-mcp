"""/health reports the proxy's own version/git_sha and each upstream's.

Fly probes /health every 30s with a 5s timeout, so the upstream view is cached
and an unreachable upstream must never change the proxy's own status.
"""

import copy
import json

import pytest

import server

# The cache exactly as server.py ships it, captured before any test touches it.
INITIAL_CACHE = copy.deepcopy(server._upstream_cache)


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    monkeypatch.setattr(server, "_upstream_cache", copy.deepcopy(INITIAL_CACHE))


def _body(resp) -> dict:
    return json.loads(resp.body)


@pytest.mark.asyncio
async def test_health_reports_proxy_and_every_upstream(monkeypatch):
    calls = []

    async def fake(client, url):
        calls.append(url)
        return {"status": "ok", "version": "9.9.9", "git_sha": "abc"}

    monkeypatch.setattr(server, "_upstream_health", fake)
    body = _body(await server.health(None))

    assert body["status"] == "ok"
    assert body["version"] == server.SERVER_VERSION
    assert body["git_sha"] == server.GIT_SHA
    assert set(body["upstreams"]) == set(server.PROXY_MOUNTS)
    assert body["upstreams"]["law"] == {"status": "ok", "version": "9.9.9", "git_sha": "abc"}
    assert sorted(calls) == sorted(server.PROXY_MOUNTS.values())


@pytest.mark.asyncio
async def test_upstream_view_is_cached(monkeypatch):
    calls = []

    async def fake(client, url):
        calls.append(url)
        return {"status": "ok", "version": None, "git_sha": None}

    monkeypatch.setattr(server, "_upstream_health", fake)
    await server.health(None)
    await server.health(None)
    assert len(calls) == len(server.PROXY_MOUNTS)


@pytest.mark.asyncio
async def test_unreachable_upstream_keeps_proxy_status_ok(monkeypatch):
    import httpx

    def handler(request):
        raise httpx.ConnectError("down", request=request)

    real = httpx.AsyncClient

    class Offline(real):
        def __init__(self, *a, **kw):
            super().__init__(*a, transport=httpx.MockTransport(handler), **kw)

    monkeypatch.setattr(server.httpx, "AsyncClient", Offline)
    body = _body(await server.health(None))

    assert body["status"] == "ok"
    assert all(u == {"status": "unreachable", "error": "ConnectError"} for u in body["upstreams"].values())



@pytest.mark.asyncio
async def test_upstreams_fetched_on_a_freshly_booted_vm(monkeypatch):
    """#13: monotonic() counts from boot. On a new Fly VM it is small, and the
    shipped cache (stamped 0.0) looked fresh for the first 60 s, so /health
    reported no upstreams. The initial state must mean 'never fetched'."""
    calls = []

    async def fake(client, url):
        calls.append(url)
        return {"status": "ok", "version": None, "git_sha": None}

    monkeypatch.setattr(server, "_upstream_health", fake)
    monkeypatch.setattr(server.time, "monotonic", lambda: 5.0)
    body = _body(await server.health(None))

    assert len(calls) == len(server.PROXY_MOUNTS)
    assert set(body["upstreams"]) == set(server.PROXY_MOUNTS)
