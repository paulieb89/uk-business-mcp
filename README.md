# UK Business MCP

One MCP server for UK business. GOV.UK, legal research, due diligence, and property data — behind a single URL.

## What's inside

This is a [FastMCP](https://gofastmcp.com) proxy that bundles four specialist UK MCP servers into one connector. Add the URL once and get access to everything.

| Prefix | Server | What it does |
|--------|--------|-------------|
| `gov_` | [GOV.UK](https://github.com/paulieb89/govuk-mcp) | Search 700k+ GOV.UK pages, retrieve content, look up organisations, resolve postcodes |
| `law_` | [UK Legal](https://github.com/paulieb89/uk-legal-mcp) | Case law, legislation, Hansard debates, HMRC guidance, OSCOLA citations |
| `dd_` | [UK Due Diligence](https://github.com/paulieb89/uk-due-diligence-mcp) | Companies House, Charity Commission, Land Registry corporate, Gazette insolvency, HMRC VAT |
| `prop_` | [UK Property](https://github.com/paulieb89/property-shared) | Land Registry, EPC, Rightmove, yields, stamp duty, planning |

## Setup

Add this URL as a custom connector in Claude.ai or Claude Desktop:

```
https://uk-business-mcp.fly.dev/mcp
```

That's it. One URL, four servers, all the UK business data tools.

### Claude.ai

1. Click **Customise** on the left panel
2. Click **Connectors** → **+** → **Add custom connector**
3. Name it anything you like, paste the URL above

### Claude Desktop / claude_desktop_config.json

```json
{
  "mcpServers": {
    "uk-business": {
      "url": "https://uk-business-mcp.fly.dev/mcp"
    }
  }
}
```

## Example tools

Once connected, you'll see tools like:

- `gov_govuk_search` — search GOV.UK pages
- `law_case_law_search` — find UK court judgments
- `law_legislation_search` — search Acts and Statutory Instruments
- `dd_company_search` — search Companies House
- `dd_charity_search` — search Charity Commission
- `prop_property_report` — full property analysis from one address
- `prop_stamp_duty` — SDLT calculator

## How it works

This server is a pure proxy — it doesn't store data or run its own tools. Every request is forwarded to the appropriate backend server. Tool lists are cached for 5 minutes.

Built with [FastMCP](https://gofastmcp.com) `create_proxy()` and `mount()`.

## Free skills

Pair these servers with free skills at [bouch.dev/tools](https://bouch.dev/tools).

## License

MIT
