# Germany MCP — submission guide (for humans and AI assistants)

How to suggest a new server (or skill) for the Germany MCP catalog at
https://mohammad-abbasi-sh.github.io/germany-mcp/ — and the standards every
entry must meet. There is no account on this site: submissions go through
GitHub Issues (the site's "Add a tool" page opens a prefilled issue).

## What the catalog accepts

- Unofficial, read-only MCP servers for German web services (news, weather,
  transport, open data, finance, housing, sports, media, language, shopping,
  health, education, travel).
- One service per server. The server reads the service's public data only.
- Agent skills are listed separately and only when they fill a proven gap.

## What it does NOT accept

- Servers that write, buy, book, or change anything in a user account.
- Servers that need an API key the user must buy, or a paid subscription.
- Servers for services that are not German / not used in Germany.
- Scrapers that ignore robots.txt or hammer a site without caching.

## Required fields (all submissions)

| Field | Limit | Notes |
|---|---|---|
| Name (EN) | 3–40 chars | e.g. "Bundesliga" |
| Name (FA) | 3–40 chars | Persian name |
| ID (slug) | auto from EN name | lowercase, hyphens, ends with `-mcp` |
| Summary | max 160 chars | one sentence, what data it reads |
| Category | one of the 13 | sports, news, media, weather, transport, open-data, language, education, shopping, health, finance, housing, travel |
| Tags | up to 5 | comma-separated, lowercase |
| Repository | GitHub URL | public, open source |
| License | SPDX id | e.g. MIT, PolyForm-Noncommercial-1.0.0 |
| Install command | `uvx <package>` | the server must run with uvx |

## Server standards

1. **Read-only.** No tool may mutate anything: no orders, no bookings, no
   messages, no account changes. If a tool needs a login, it does not belong.
2. **No API key.** The server works with zero configuration after `uvx`.
3. **Real tests.** Every tool is exercised against the live service (or a
   recorded fixture) and the tests pass. Untested servers are not published.
4. **Trilingual.** English + German + Persian: server description and every
   tool summary in all three languages.
5. **Honest numbers.** No fabricated data, no guessed prices, no stale
   snapshots presented as live. If a value can be a paywall or an estimate,
   say so in the tool output.
6. **Caching.** Read endpoints are cached (at least 60 seconds) so the
   assistant does not hammer the source site.
7. **License + source.** Public repo, open-source license, README with
   install + tool list + limits.

## How to submit

1. Open the catalog's "Add a tool" page (`#/en/submit`) and fill the form —
   or open an issue directly at
   https://github.com/mohammad-abbasi-sh/germany-mcp/issues/new with the
   fields above.
2. The form can autofill name, description and license from a public GitHub
   repo URL (it reads GitHub's public API in your browser).
3. Review is manual: the maintainer checks the repo, runs the tests, and
   either publishes the server or asks for changes in the issue. There is no
   automatic acceptance and no queue to watch — the issue is the thread.

## Common rejections (avoid these)

- "Works on my machine" with no tests.
- Tool summaries in English only.
- A server that wraps a paid API and asks the user for a key.
- Copying another catalog's server without attribution or a real difference.
- A README that does not say what the server cannot do.

## For AI assistants (copy-paste brief)

> Suggest a Germany MCP server: read-only, uvx-runnable, no API key, real
> tests, EN/DE/FA descriptions, open-source repo. Fill the "Add a tool" form
> with: EN name, FA name, 160-char summary, one category, up to 5 tags,
> GitHub repo URL, license, install command. Then open the prefilled GitHub
> issue and wait for manual review.
