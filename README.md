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
| [ntv-mcp](https://github.com/mohammad-abbasi-sh/ntv-mcp) | n-tv — German TV news: headlines by section, markets, videos & articles | 5 | `uvx ntv-mcp==0.1.0` |
| [dnb-mcp](https://github.com/mohammad-abbasi-sh/dnb-mcp) | DNB — Deutsche Nationalbibliothek catalogue: books, authors & ISBN lookup | 5 | `uvx dnb-mcp==0.1.0` |
| [govdata-mcp](https://github.com/mohammad-abbasi-sh/govdata-mcp) | GovData — Germany's open-data portal: search 163,000+ datasets, publishers & resources | 5 | `uvx govdata-mcp==0.1.0` |
| [deutschlandfunk-mcp](https://github.com/mohammad-abbasi-sh/deutschlandfunk-mcp) | Deutschlandfunk — German public radio news: rolling news, topics, articles & live stream | 6 | `uvx deutschlandfunk-mcp==0.1.0` |
| [duden-mcp](https://github.com/mohammad-abbasi-sh/duden-mcp) | Duden — Germany's standard dictionary: word meanings, synonyms, spelling & grammar | 6 | `uvx duden-mcp==0.1.0` |
| [dictcc-mcp](https://github.com/mohammad-abbasi-sh/dictcc-mcp) | dict.cc — German-English & 22 more pairs: translations with word class, gender & votes | 2 | `uvx dictcc-mcp==0.1.0` |
| [bundeswahlleiter-mcp](https://github.com/mohammad-abbasi-sh/bundeswahlleiter-mcp) | Bundeswahlleiterin — German federal election results: Bundestag elections 2017–2025 | 5 | `uvx bundeswahlleiter-mcp==0.1.0` |
| [flixtrain-mcp](https://github.com/mohammad-abbasi-sh/flixtrain-mcp) | FlixTrain — train times, stations & prices between German cities | 2 | `uvx flixtrain-mcp==0.1.0` |
| [billiger-mcp](https://github.com/mohammad-abbasi-sh/billiger-mcp) | billiger.de — German price comparison: best prices, shop offers & deals | 3 | `uvx billiger-mcp==0.1.0` |
| [fernsehserien-mcp](https://github.com/mohammad-abbasi-sh/fernsehserien-mcp) | fernsehserien.de — German TV series: search, details, episodes & air dates | 4 | `uvx fernsehserien-mcp==0.1.0` |
| [zdf-mcp](https://github.com/mohammad-abbasi-sh/zdf-mcp) | ZDF heute news — headlines, topics, search & articles | 4 | `uvx zdf-mcp==0.1.0` |
| [ecb-mcp](https://github.com/mohammad-abbasi-sh/ecb-mcp) | ECB euro data — exchange rates, key rates, inflation, money supply & bond yields | 5 | `uvx ecb-mcp==0.1.0` |
| [wg-gesucht-mcp](https://github.com/mohammad-abbasi-sh/wg-gesucht-mcp) | WG-Gesucht housing — rooms & flats in German cities | 4 | `uvx wg-gesucht-mcp==0.1.0` |
| [uba-mcp](https://github.com/mohammad-abbasi-sh/uba-mcp) | UBA — German air quality: hourly PM10, NO2, O3 values + LQI from 400+ stations | 6 | `uvx uba-mcp==0.1.0` |
| [openplz-mcp](https://github.com/mohammad-abbasi-sh/openplz-mcp) | OpenPLZ — German postal codes: PLZ lookup, streets & admin tree | 6 | `uvx openplz-mcp==0.1.0` |
| [feiertage-mcp](https://github.com/mohammad-abbasi-sh/feiertage-mcp) | Feiertage — German public holidays: by year & state, is-it-a-holiday, next holiday | 5 | `uvx feiertage-mcp==0.1.0` |
| [ferien-mcp](https://github.com/mohammad-abbasi-sh/ferien-mcp) | Ferien — German school holidays: by year & state, is-it-a-holiday, next holiday | 5 | `uvx ferien-mcp==0.1.0` |

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
