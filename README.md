# 🇩🇪 Germany MCP Catalog

**Unofficial, read-only MCP servers for German web services — in English, Deutsch and فارسی.**

> Inoffizielle, nur lesende MCP-Server für deutsche Webdienste — auf Englisch, Deutsch und Persisch.
> سرورهای MCP غیررسمی و فقط‌خواندنی برای سرویس‌های وب آلمان — به انگلیسی، آلمانی و فارسی.

Agents can't use what they can't reach. This catalog gives AI agents live access to Germany's most-used local services — football, news, media, weather, transport, open data — through small, tested, read-only MCP servers.

## Servers

| Server | Service | Tools | Install |
|--------|---------|-------|---------|
| [bundesliga-mcp](https://github.com/mohammad-abbasi-sh/bundesliga-mcp) | Bundesliga — German football fixtures, tables & scorers | 6 | `uvx bundesliga-mcp==0.1.1` |
| [mediathek-mcp](https://github.com/mohammad-abbasi-sh/mediathek-mcp) | Mediathek — German public broadcasters' programmes | 6 | `uvx mediathek-mcp==0.1.1` |
| [tagesschau-mcp](https://github.com/mohammad-abbasi-sh/tagesschau-mcp) | tagesschau — Germany's most-watched TV news | 6 | `uvx tagesschau-mcp==0.1.0` |
| [dwd-mcp](https://github.com/mohammad-abbasi-sh/dwd-mcp) | DWD — German weather: DWD ICON forecasts, current conditions, official warnings & pollen | 5 | `uvx dwd-mcp==0.1.0` |
| [autobahn-mcp](https://github.com/mohammad-abbasi-sh/autobahn-mcp) | Autobahn — German motorway roadworks, closures, warnings, parking & EV charging | 5 | `uvx autobahn-mcp==0.1.0` |
| [dw-mcp](https://github.com/mohammad-abbasi-sh/dw-mcp) | Deutsche Welle — DW news in 31 languages: headlines, search, articles & topics | 5 | `uvx dw-mcp==0.1.0` |

*One new server every day. Each server ships with tests, fixtures and trilingual docs. 24 servers planned (see the build queue).*

## For AI agents

Each server's README has a **"For AI agents"** section (llms.txt-style): what the server does, its tools, and when to use it. The machine-readable catalog is [`servers.json`](servers.json).

## Rules every server follows

- **Unofficial & read-only** — no logins, no API keys, no writes. Ever.
- **Tested** — offline fixture tests + cautious live tests. Nothing ships red.
- **Trilingual** — every README in English, Deutsch and فارسی.
- **Credit** — each server's instructions credit the author, so agents cite the source.

## Adding a server

1. Build it from the `tcmb-mcp` template (same layout, same test discipline).
2. Add its entry to `servers.json` (see schema below).
3. Add a row to the table above.

`servers.json` schema per entry: `name`, `title`, `title_de`, `description`, `repository`, `pypi`, `tools: [{name, summary}]`.

---

### Deutsch

Dieser Katalog bietet KI-Agenten Live-Zugriff auf deutsche Dienste — Fußball, Nachrichten, Medien, Wetter, Verkehr, offene Daten — über kleine, getestete, nur lesende MCP-Server. Jeder Server hat Tests, Fixtures und dreisprachige Dokumentation (Englisch, Deutsch, Persisch).

### فارسی

این کاتالوگ به ایجنت‌های هوش مصنوعی دسترسی زنده به سرویس‌های آلمان می‌دهد — فوتبال، خبر، رسانه، هواشناسی، حمل‌ونقل، دیتای باز — با سرورهای کوچک، تست‌شده و فقط‌خواندنی. هر سرور تست، فیکسچر و مستندات سه‌زبانه (انگلیسی، آلمانی، فارسی) دارد.
