from fastmcp import FastMCP
from fastmcp.server import create_proxy
from starlette.responses import JSONResponse

mcp = FastMCP(
    "UK Business",
    instructions=(
        "Ledgerhall: UK public data for AI agents. Four upstream namespaces:\n"
        "\n"
        "  gov_*   — GOV.UK: 700k+ pages, organisations, postcodes\n"
        "  law_*   — UK Legal: case law, legislation, Hansard, HMRC guidance, OSCOLA\n"
        "  dd_*    — Due Diligence: Companies House, Charity Commission, Land Registry, Gazette, VAT\n"
        "  prop_*  — Property: Land Registry, EPC, Rightmove, yields, stamp duty, planning\n"
        "\n"
        "Due-diligence resources — use dd_list_resources to discover, dd_read_resource to fetch.\n"
        "Pass the URI exactly as returned by dd_list_resources (no dd/ prefix):\n"
        "  company://{company_number}/profile   — Companies House profile\n"
        "  company://{company_number}/officers  — active officers\n"
        "  company://{company_number}/psc       — persons with significant control\n"
        "  disqualification://{officer_id}      — disqualification record\n"
        "  charity://{charity_number}/profile   — Charity Commission profile"
    ),
)

mcp.mount(create_proxy("https://govuk-mcp.fly.dev/mcp"), namespace="gov")
mcp.mount(create_proxy("https://uk-legal-mcp.fly.dev/mcp"), namespace="law")
mcp.mount(create_proxy("https://uk-due-diligence-mcp.fly.dev/mcp"), namespace="dd")
mcp.mount(create_proxy("https://property-shared.fly.dev/mcp"), namespace="prop")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


def main():
    import uvicorn
    # stateless_http=True: each request creates a fresh transport context.
    # Required for aggregator proxies (Lesson 32) and multi-machine Fly
    # deploys (Lesson 2) — without it, clients hit "Missing session ID"
    # on any request not preceded by initialize on the same machine.
    uvicorn.run(mcp.http_app(stateless_http=True), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
