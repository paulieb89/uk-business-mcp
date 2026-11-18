"""/health reports the proxy's own version/git_sha and each upstream's.

Fly probes /health every 30s with a 5s timeout, so the upstream view is cached
and an unreachable upstream must never change the proxy's own status.
"""

import json

import pytest

import server


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    monkeypatch.setattr(server, "_upstream_cache", {"at": 0.0, "data": {}})


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
