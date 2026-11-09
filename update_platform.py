#!/usr/bin/env python3
"""Regenerate the Germany MCP platform (platform/index.html) from servers.json.

Reads the template platform/base.html (built once by migrate_from_turkey.py
from the Turkey v6 platform — never hand-edit the generated index.html),
fills the SERVERS array from servers.json, flips category soon-flags for
categories that have live servers, and fills the __COUNTS_*__ tokens with
computed counts (never hardcoded).

EN titles/descriptions/tool summaries come from servers.json; FA/DE strings
are authored in TRANSLATIONS below (no machine output, no fabricated
numbers). When the factory adds a server: add its entry to SERVER_META
(cat/color/letter/featured) and TRANSLATIONS, then re-run this script.

Usage: python3 update_platform.py
Output: platform/index.html (+ versioned copy platform/index-v1-20261109.html)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "servers.json").read_text())
BY_ID = {s["name"]: s for s in DATA["servers"]}

# Per-server platform metadata. cat must match a CATEGORIES id in base.html.
# added = catalog order (1-based). featured: only the flagship server(s).
SERVER_META = {
    "bundesliga-mcp": {"cat": "sports", "color": "#15803D", "letter": "⚽",
                       "featured": True, "added": 1},
    "mediathek-mcp": {"cat": "media", "color": "#9F1239", "letter": "📺",
                      "featured": False, "added": 2},
}

# FA/DE authorship: desc_fa, desc_de, and per-tool (sf, st) keyed by tool name.
TRANSLATIONS = {
"bundesliga-mcp": {
 "desc_fa": "بوندس‌لیگا، لیگ ۲ و ۳، جام حذفی و DEL با OpenLigaDB (API رایگان، بدون کلید): بازی‌ها، نتایج زنده، جدول‌ها و گلزنان برتر.",
 "desc_de": "Bundesliga, 2. und 3. Liga, DFB-Pokal und DEL über OpenLigaDB (kostenlose API, kein Schlüssel): Spielpläne, Live-Ergebnisse, Tabellen und Torschützen.",
 "tools": {
  "bundesliga_list_leagues": ("لیگ‌ها با فصل جاری", "Ligen mit ihrer aktuellen Saison"),
  "bundesliga_get_fixtures": ("بازی‌های یک هفتهٔ مشخص با نتایج", "Spiele eines Spieltags mit Ergebnissen"),
  "bundesliga_get_live_scores": ("نتایج زندهٔ هفتهٔ جاری", "Aktuelle Live-Ergebnisse des Spieltags"),
  "bundesliga_get_table": ("جدول لیگ", "Tabelle der Liga"),
  "bundesliga_get_top_scorers": ("گلزنان برتر یک فصل", "Torschützen einer Saison"),
  "bundesliga_get_match_detail": ("جزئیات کامل یک مسابقه", "Vollständige Details eines Spiels"),
 }},
"mediathek-mcp": {
 "desc_fa": "ARD، ZDF، 3sat، ARTE، Phoenix و بیشتر با MediathekViewWeb (API رایگان، بدون کلید): جست‌وجوی برنامه‌ها، جدیدترین پخش‌ها، بر اساس شبکه/موضوع و جزئیات برنامه.",
 "desc_de": "ARD, ZDF, 3sat, ARTE, Phoenix und mehr über MediathekViewWeb (kostenlose API, kein Schlüssel): Sendungen suchen, neueste Sendungen, nach Sender/Thema, Sendedetails.",
 "tools": {
  "mediathek_search_programmes": ("جست‌وجوی برنامه‌ها با عنوان، موضوع یا توضیح", "Sendungen nach Titel, Thema oder Beschreibung suchen"),
  "mediathek_latest_broadcasts": ("جدیدترین برنامه‌های همهٔ شبکه‌ها", "Neueste Sendungen aller Sender"),
  "mediathek_by_channel": ("جدیدترین برنامه‌های یک شبکه", "Neueste Sendungen eines Senders"),
  "mediathek_by_topic": ("همهٔ قسمت‌های یک برنامه یا سریال", "Alle Folgen einer Sendung oder Serie"),
  "mediathek_programme_detail": ("جزئیات کامل یک برنامه (لینک ویدیو، زیرنویس)", "Vollständige Details einer Sendung (Video-URLs, Untertitel)"),
  "mediathek_list_channels": ("شبکه‌های فهرست فیلم", "Sender der Filmliste"),
 }},
}

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def fa_num(n):
    return str(n).translate(FA_DIGITS)


def js_str(s):
    """Double-quoted JS string literal (data contains no double quotes)."""
    assert '"' not in s, f"double quote in string: {s}"
    return '"' + s.replace("\\", "\\\\") + '"'


def build_entry(name):
    src = BY_ID[name]
    meta = SERVER_META[name]
    tr = TRANSLATIONS[name]
    assert set(tr["tools"]) == {t["name"] for t in src["tools"]}, name
    lines = []
    lines.append('{ id:%s, cat:%s, color:%s, letter:%s, featured:%s, added:%d,' % (
        js_str(name), js_str(meta["cat"]), js_str(meta["color"]),
        js_str(meta["letter"]), "true" if meta["featured"] else "false",
        meta["added"]))
    lines.append('  title:%s,' % js_str(src["title"]))
    lines.append('  title_de:%s,' % js_str(src["title_de"]))
    lines.append('  desc:%s,' % js_str(src["description"]))
    lines.append('  desc_fa:%s,' % js_str(tr["desc_fa"]))
    lines.append('  desc_de:%s,' % js_str(tr["desc_de"]))
    lines.append('  repo:%s, pypi:%s,' % (
        js_str(src["repository"]), js_str(src["pypi"])))
    lines.append('  tools:[')
    for i, t in enumerate(src["tools"]):
        sf, st = tr["tools"][t["name"]]
        comma = "," if i < len(src["tools"]) - 1 else ""
        lines.append('   {n:%s,s:%s,sf:%s,st:%s}%s' % (
            js_str(t["name"]), js_str(t["summary"]), js_str(sf), js_str(st),
            comma))
    lines.append('  ]}')
    return "\n".join(lines)


def main():
    base_path = HERE / "platform" / "base.html"
    html = base_path.read_text()
    assert "const SERVERS = [];" in html, "base.html has no empty SERVERS array"

    # --- 1. SERVERS array from servers.json, in catalog order ---
    order = sorted(BY_ID, key=lambda n: SERVER_META[n]["added"])
    entries = [build_entry(n) for n in order]
    html = html.replace("const SERVERS = [];",
                        "const SERVERS = [\n" + ",\n".join(entries) + "\n];", 1)

    # --- 2. CATEGORIES soon-flags: false for categories with live servers ---
    live_cats = {SERVER_META[n]["cat"] for n in order}

    def flip(m):
        cid = m.group(1)
        return '{id:"%s",icon:"%s",color:"%s",soon:%s},' % (
            cid, m.group(2), m.group(3),
            "false" if cid in live_cats else "true")

    html, n = re.subn(
        r'\{id:"([a-z-]+)",icon:"([^"]+)",color:"(#[0-9A-Fa-f]+)",soon:(?:true|false)\},',
        flip, html)
    assert n == 13, f"expected 13 CATEGORIES lines, found {n}"

    # --- 3. Counts tokens -> computed counts (never hardcoded) ---
    n_servers = len(order)
    n_tools = sum(len(BY_ID[n]["tools"]) for n in order)
    counts = {
        "__COUNTS_FA__": "%s سرور، %s ابزار" % (fa_num(n_servers), fa_num(n_tools)),
        "__COUNTS_DE__": "%d Server, %d Tools" % (n_servers, n_tools),
        "__COUNTS_EN__": "%d server%s, %d tools" % (
            n_servers, "" if n_servers == 1 else "s", n_tools),
    }
    for tok, val in counts.items():
        assert tok in html, f"missing token {tok}"
        html = html.replace(tok, val)

    # --- Validation ---
    assert "__COUNTS_" not in html, "unfilled count token left"
    bad = [s for s in ("Turkey", "Türkiye", "Türkçe", "Turkish", "tcmb",
                       "Hepsiburada", "obilet", "arabam", "emlakjet", "armut",
                       "n11", "ciceksepeti", "biletall", "secretcv", "biletix",
                       "sozcu", "eleman", "mackolik", "donanimhaber",
                       "yemek.com", "hurriyet", "sok-mcp", "jolly", "migros",
                       "cineverse", "trthaber", "22 servers", "111 tools",
                       '"tr"', "'tr'", "tr:", "title_tr", "desc_tr",
                       "tag_tr", "gap_tr", "ترکیه")
           if s in html]
    assert not bad, f"Turkish/Turkey leftovers: {bad}"
    assert html.count("{ id:") == n_servers, "SERVERS entry count mismatch"
    assert html.count("{n:") == n_tools, "tool entry count mismatch"

    # node --check on the extracted <script>
    m = re.search(r"<script>(.*?)</script>", html, re.S)
    assert m, "no <script> block found"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
        f.write(m.group(1))
        js_path = f.name
    r = subprocess.run(["node", "--check", js_path], capture_output=True,
                       text=True)
    assert r.returncode == 0, f"node --check failed: {r.stderr}"

    out = HERE / "platform" / "index.html"
    out.write_text(html)
    versioned = HERE / "platform" / "index-v1-20261109.html"
    versioned.write_text(html)
    print("wrote", out, len(html), "chars;",
          n_servers, "server(s),", n_tools, "tools; node --check OK")


if __name__ == "__main__":
    main()
