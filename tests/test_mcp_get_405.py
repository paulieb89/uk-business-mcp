"""/mcp is stateless POST-only: GET is refused with FastMCP's native 405 (#12).

uk-due-diligence-mcp and uk-legal-mcp dropped the held-open GET stream shim after
interoperability testing (Claude Code, Codex, claude.ai web, ChatGPT web all work
with the native 405). The shim held a connection open per GET with nothing sent;
this proxy now matches them. The Accept normaliser is a separate concern and stays.
"""

from starlette.testclient import TestClient

import server

INIT = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}},
}


def test_get_mcp_is_refused_with_405_and_allows_post():
    with TestClient(server.create_app()) as c:
        resp = c.get("/mcp", headers={"Accept": "text/event-stream"})

    assert resp.status_code == 405
    assert "POST" in resp.headers["allow"]


def test_post_initialize_succeeds_without_any_get_stream():
    with TestClient(server.create_app()) as c:
        resp = c.post(
            "/mcp", json=INIT,
            headers={"Accept": "application/json, text/event-stream", "Content-Type": "application/json"},
        )

    assert resp.status_code == 200
    assert resp.json()["result"]["serverInfo"]["name"]


def test_accept_normaliser_still_admits_a_bare_accept_header():
    with TestClient(server.create_app()) as c:
        resp = c.post("/mcp", json=INIT, headers={"Accept": "application/json", "Content-Type": "application/json"})

    assert resp.status_code == 200
