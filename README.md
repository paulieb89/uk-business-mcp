# Ledgerhall

**UK public data for AI agents.** One connection. Companies House, Land Registry, GOV.UK, courts, Parliament — your agent gets the lot.

```
https://uk-business-mcp.fly.dev/mcp
```

No API key. No account. Free and hosted.

[Set up in 30 seconds →](https://bouch.dev/ledgerhall/)

---

## What you can do

Once connected, your AI agent can:

- **Check any UK company** — directors, shareholders, filing history, disqualified officers
- **Research property** — comparable sales, EPC ratings, Rightmove listings, rental yields, stamp duty
- **Search case law and legislation** — court judgments, Acts, Hansard debates, HMRC guidance
- **Query GOV.UK** — search 700k+ pages, resolve postcodes to councils, find policy documents
- **Run due diligence** — cross-reference Companies House, Charity Commission, Land Registry, Gazette insolvency, VAT records

## Setup

### claude.ai

1. Go to **Settings** (bottom left)
2. Click **MCP Servers**
3. Click **Add**
4. Paste: `https://uk-business-mcp.fly.dev/mcp`

### Claude Desktop

Add to `claude_desktop_config.json`:

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

### Claude Code

```bash
claude mcp add --transport http ledgerhall https://uk-business-mcp.fly.dev/mcp
```

### ChatGPT

1. Go to **Settings** → **Connected apps** → **Add MCP server**
2. Paste: `https://uk-business-mcp.fly.dev/mcp`

### Cursor / other editors

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ledgerhall": {
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
| `dd_` | [UK Due Diligence](https://github.com/paulieb89/uk-due-diligence-mcp) | Companies House, Charity Commission, Land Registry, Gazette, VAT |
| `prop_` | [UK Property](https://github.com/paulieb89/property-shared) | Land Registry, EPC, Rightmove, yields, stamp duty, planning |

## How it works

Pure proxy — no data storage, no custom tools. Every request is forwarded to the appropriate backend. Tool lists are cached for 5 minutes. Built with FastMCP `create_proxy()` and `mount()`.

## Coming next

- **UK Compliance** — FCA Register and SRA solicitor checks
- **UK Statistics** — ONS economic data and Nomis labour market profiles

New servers appear automatically. No config changes needed.

## Links

- **Product page:** [bouch.dev/ledgerhall](https://bouch.dev/ledgerhall/)
- **Free AI skills:** [bouch.dev/tools](https://bouch.dev/tools/)
- **Built by:** [BOUCH](https://bouch.dev) — AI consultancy, East Midlands

## License

MIT
