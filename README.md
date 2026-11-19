# Ledgerhall

Maintained by BOUCH — private hosting, custom tools and setup: paul@bouch.dev · [bouch.dev/products/uk-business-mcp](https://bouch.dev/products/uk-business-mcp)

<!-- mcp-name: io.github.paulieb89/uk-business-mcp -->

[![Glama](https://img.shields.io/badge/Glama-listed-orange?style=flat-square)](https://glama.ai/mcp/connectors/dev.fly.uk-business-mcp/uk-business-tools-ledgerhall)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://vscode.dev/redirect/mcp/install?name=ledgerhall&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fuk-business-mcp.fly.dev%2Fmcp%22%7D)
[![Install in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Install_Server-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=ledgerhall&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fuk-business-mcp.fly.dev%2Fmcp%22%7D&quality=insiders)
[![Install in Cursor](https://img.shields.io/badge/Cursor-Install_Server-000000?style=flat-square&logoColor=white)](https://cursor.com/en/install-mcp?name=ledgerhall&config=eyJ0eXBlIjoiaHR0cCIsInVybCI6Imh0dHBzOi8vdWstYnVzaW5lc3MtbWNwLmZseS5kZXYvbWNwIn0=)

**UK public data for AI agents.** One connection. Companies House, Land Registry, GOV.UK, courts, Parliament — your agent gets the lot.

```
https://uk-business-mcp.fly.dev/mcp
```

No API key. No account. Free and hosted.

[Set up in 30 seconds →](https://bouch.dev/products/uk-business-mcp)

---

## What you can do

Once connected, your AI agent can:

- **Check any UK company** — directors, shareholders, filing history, disqualified officers
- **Research property** — comparable sales, EPC ratings, Rightmove listings, rental yields, stamp duty
- **Search case law and legislation** — court judgments, Acts, Hansard debates, HMRC guidance
- **Query GOV.UK** — search 700k+ pages, resolve postcodes to councils, find policy documents
- **Run due diligence** — cross-reference Companies House, Charity Commission, Land Registry, Gazette insolvency, sanctions lists

## Connect

Hosted endpoint — no install, no API key:

```text
https://uk-business-mcp.fly.dev/mcp
```

### Claude (web, desktop and mobile)

1. Open **Customize → Connectors** ([claude.ai/customize/connectors](https://claude.ai/customize/connectors)).
2. Click **Add custom connector**.
3. Name it `ledgerhall`, paste the URL above and click **Add**. No sign-in is needed.

That's it — no config file to edit and no restart. Add the connector on web or desktop, and it's then available on your account, including the mobile apps. Turn it on or off per chat from the **+** menu → **Connectors**. On Team and Enterprise plans an Owner adds it once under **Organization settings → Connectors**; Free plans can add one custom connector.

### Claude Code

If you've added the connector above, Claude Code lists it under `/mcp` — but only when Claude Code is signed in with your claude.ai subscription login, not an API key. Otherwise, add it directly:

```bash
claude mcp add --transport http --scope user ledgerhall https://uk-business-mcp.fly.dev/mcp
```

### ChatGPT

Turn on **Developer mode** (Settings → Apps & Connectors → Advanced settings), then **Create** a connector and paste the URL above. OpenAI moves these menus around; see their [developer mode guide](https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt) if a label doesn't match.

### Other clients

For Cursor (`.cursor/mcp.json`) and other clients configured with `mcpServers` JSON:

```json
{
  "mcpServers": {
    "ledgerhall": {
      "type": "http",
      "url": "https://uk-business-mcp.fly.dev/mcp"
    }
  }
}
```

## What's inside

Ledgerhall is a [FastMCP](https://gofastmcp.com) proxy that bundles four specialist UK MCP servers into one endpoint. Each server covers a different part of the UK public record.

| Prefix | Server | Coverage |
|--------|--------|----------|
| `gov_` | [GOV.UK](https://github.com/paulieb89/govuk-mcp) | 700k+ GOV.UK pages, organisations, postcodes |
| `law_` | [UK Legal](https://github.com/paulieb89/uk-legal-mcp) | Case law, legislation, Hansard, HMRC guidance, OSCOLA |
| `dd_` | [UK Due Diligence](https://github.com/paulieb89/uk-due-diligence-mcp) | Companies House, Charity Commission, Land Registry, Gazette, sanctions |
| `prop_` | [UK Property](https://github.com/paulieb89/property-shared) | Land Registry, EPC, Rightmove, yields, stamp duty, planning |

## How it works

Pure proxy — no data storage, no custom tools. Every request is forwarded to the appropriate backend. Tool lists are cached for 5 minutes. Built with FastMCP `create_proxy()` and `mount()`.

## Coming next

- **UK Compliance** — FCA Register and SRA solicitor checks
- **UK Statistics** — ONS economic data and Nomis labour market profiles

New servers appear automatically. No config changes needed.

## Links

- **Product page:** [bouch.dev/products/uk-business-mcp](https://bouch.dev/products/uk-business-mcp)
- **Free AI skills:** [bouch.dev/tools](https://bouch.dev/tools)
- **All servers:** [bouch.dev/products](https://bouch.dev/products)
- **Built by:** [BOUCH](https://bouch.dev) — AI consultancy, East Midlands

## License

MIT
