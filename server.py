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
        "Due-diligence resources (read by URI after searching with dd_company_search etc.):\n"
        "  company://dd/{company_number}/profile   — Companies House profile\n"
        "  company://dd/{company_number}/officers  — active officers\n"
        "  company://dd/{company_number}/psc       — persons with significant control\n"
        "  disqualification://dd/{officer_id}      — disqualification record\n"
        "  charity://dd/{charity_number}/profile   — Charity Commission profile\n"
        "\n"
        "For tool-only clients: dd_list_resources and dd_read_resource are available."
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
