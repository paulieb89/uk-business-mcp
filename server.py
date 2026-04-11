from fastmcp import FastMCP
from fastmcp.server import create_proxy
from starlette.responses import JSONResponse

mcp = FastMCP("UK Business")

mcp.mount(create_proxy("https://govuk-mcp.fly.dev/mcp"), namespace="gov")
mcp.mount(create_proxy("https://uk-legal-mcp.fly.dev/mcp"), namespace="law")
mcp.mount(create_proxy("https://uk-due-diligence-mcp.fly.dev/mcp"), namespace="dd")
mcp.mount(create_proxy("https://property-shared.fly.dev/mcp"), namespace="prop")


@mcp.custom_route("/health", methods=["GET"])
async def health(request):
    return JSONResponse({"status": "ok"})


def main():
    import uvicorn
    uvicorn.run(mcp.http_app(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
