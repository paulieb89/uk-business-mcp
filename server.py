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
        "Due diligence workflow — search first, then fetch detail:\n"
        "  dd_company_search    → find a company, get company_number\n"
        "  dd_company_profile   → full CH profile (status, address, SIC, filing flags)\n"
        "  dd_company_officers  → active directors with nominee risk flag\n"
        "  dd_company_psc       → persons with significant control\n"
        "  dd_charity_search    → find a charity, get charity_number\n"
        "  dd_charity_profile   → full Charity Commission profile\n"
        "  dd_disqualified_search / dd_disqualified_profile → banned directors\n"
        "  dd_gazette_insolvency / dd_gazette_notice → insolvency notices\n"
        "  dd_land_title_search → HMLR title register\n"
        "  dd_vat_validate      → HMRC VAT number check"
    ),
)

mcp.mount(create_proxy("https://govuk-mcp.fly.dev/mcp"), namespace="gov")
mcp.mount(create_proxy("https://uk-legal-mcp.fly.dev/mcp"), namespace="law")
mcp.mount(create_proxy("https://uk-due-diligence-mcp.fly.dev/mcp"), namespace="dd")
mcp.mount(create_proxy("https://property-shared.fly.dev/mcp"), namespace="prop")


@mcp.custom_route("/.well-known/mcp/server-card.json", methods=["GET"])
async def smithery_server_card(request):
    return JSONResponse({"serverInfo": {"name": "uk-business-mcp", "version": "0.1.0"}})


@mcp.custom_route("/.well-known/glama.json", methods=["GET"])
async def glama_claim(request):
    return JSONResponse({
        "$schema": "https://glama.ai/mcp/schemas/connector.json",
        "maintainers": [{"email": "paul@bouch.dev"}],
    })


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


def main():
    import uvicorn
    # stateless_http=True: each request creates a fresh transport context.
    # Required for aggregator proxies (Lesson 32) and multi-machine Fly
    # deploys (Lesson 2) — without it, clients hit "Missing session ID"
    # on any request not preceded by initialize on the same machine.
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(mcp.http_app(stateless_http=True), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
