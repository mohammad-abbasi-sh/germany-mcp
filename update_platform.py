#!/usr/bin/env python3
"""Regenerate the Germany MCP platform (platform/index.html) from servers.json.

Reads the template platform/base.html (built once by migrate_from_turkey.py
from the Turkey v6 platform — never hand-edit the generated index.html),
fills the SERVERS array from servers.json, flips category soon-flags for
categories that have live servers, and fills the __COUNTS_*__ tokens with
computed counts (never hardcoded).

DESIGN/GUIDE EDITS BELONG IN platform/base.html, NOT in this file and NOT
in the generated platform/index.html: this script contains no HTML/CSS/JS,
it only injects data into the template. Any change made only to index.html
is wiped by the next factory run; a change to base.html survives every
regeneration. (Redesign + two-track connect guide landed 2026-11-16.)

EN titles/descriptions/tool summaries come from servers.json; FA/DE strings
are authored in TRANSLATIONS below (no machine output, no fabricated
numbers). When the factory adds a server: add its entry to SERVER_META
(cat/color/letter/featured) and TRANSLATIONS, then re-run this script.

Usage: python3 update_platform.py
Output: platform/index.html (+ versioned copy) + .mcp.json, llms.txt,
llms-full.txt, catalog.json, search.json, sitemap.xml, robots.txt at root
"""
import datetime
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
    "tagesschau-mcp": {"cat": "news", "color": "#1E40AF", "letter": "📰",
                       "featured": False, "added": 3},
    "dwd-mcp": {"cat": "weather", "color": "#0284C7", "letter": "🌤️",
                 "featured": False, "added": 4},
    "autobahn-mcp": {"cat": "transport", "color": "#0369A1", "letter": "🛣️",
                     "featured": False, "added": 5},
    "dw-mcp": {"cat": "news", "color": "#0E7490", "letter": "📰",
               "featured": False, "added": 6},
    "ntv-mcp": {"cat": "news", "color": "#B91C1C", "letter": "📺",
               "featured": False, "added": 7},
    "dnb-mcp": {"cat": "open-data", "color": "#7C3AED", "letter": "📚",
               "featured": False, "added": 8},
    "govdata-mcp": {"cat": "open-data", "color": "#065F46", "letter": "🗃️",
                   "featured": False, "added": 9},
    "deutschlandfunk-mcp": {"cat": "news", "color": "#1E3A8A", "letter": "📻",
                          "featured": False, "added": 10},
    "duden-mcp": {"cat": "language", "color": "#7C3AED", "letter": "📖",
               "featured": False, "added": 11},
    "dictcc-mcp": {"cat": "language", "color": "#0E7490", "letter": "🌐",
                "featured": False, "added": 12},
    "bundeswahlleiter-mcp": {"cat": "open-data", "color": "#92400E", "letter": "🗳️",
                          "featured": False, "added": 13},
    "flixtrain-mcp": {"cat": "transport", "color": "#B45309", "letter": "🚆",
                   "featured": False, "added": 14},
    "billiger-mcp": {"cat": "shopping", "color": "#1D4ED8", "letter": "🛒",
                  "featured": False, "added": 15},
    "fernsehserien-mcp": {"cat": "media", "color": "#7C2D12", "letter": "📺",
                       "featured": False, "added": 16},
    "zdf-mcp": {"cat": "media", "color": "#C8102E", "letter": "📺",
             "featured": False, "added": 17},
    "ecb-mcp": {"cat": "finance", "color": "#003399", "letter": "💶",
             "featured": False, "added": 18},
    "wg-gesucht-mcp": {"cat": "housing", "color": "#0E7490", "letter": "🏠",
                    "featured": False, "added": 19},
    "uba-mcp": {"cat": "health", "color": "#059669", "letter": "🌬️",
                "featured": False, "added": 20},
    "openplz-mcp": {"cat": "open-data", "color": "#0F766E", "letter": "🧭",
                    "featured": False, "added": 21},
    "feiertage-mcp": {"cat": "open-data", "color": "#9D174D", "letter": "📅",
                      "featured": False, "added": 22},
    "ferien-mcp": {"cat": "open-data", "color": "#EA580C", "letter": "🏖️",
                   "featured": False, "added": 23},
    "spiegel-mcp": {"cat": "news", "color": "#E2001A", "letter": "🗞️",
                    "featured": False, "added": 24},
    "heise-mcp": {"cat": "news", "color": "#00559F", "letter": "💻",
                  "featured": False, "added": 25},
    "zeit-mcp": {"cat": "news", "color": "#9B1B30", "letter": "⏰",
                 "featured": False, "added": 26},
    "welt-mcp": {"cat": "news", "color": "#0F172A", "letter": "🌍",
                 "featured": False, "added": 27},
    "ndr-mcp": {"cat": "news", "color": "#003A70", "letter": "📡",
                "featured": False, "added": 28},
    "br-mcp": {"cat": "news", "color": "#0B5FA5", "letter": "📻",
               "featured": False, "added": 29},
    "focus-online-mcp": {"cat": "news", "color": "#E30613", "letter": "📰",
               "featured": False, "added": 30},
    "bundesregierung-mcp": {"cat": "news", "color": "#111827", "letter": "🏛️",
               "featured": False, "added": 31},
    "mdr-mcp": {"cat": "news", "color": "#1E3A5F", "letter": "🎙️",
               "featured": False, "added": 32},
    "bild-mcp": {"cat": "news", "color": "#C00000", "letter": "📰",
               "featured": False, "added": 33},
    "taz-mcp": {"cat": "news", "color": "#A6192E", "letter": "📰",
               "featured": False, "added": 34},
    "t3n-mcp": {"cat": "news", "color": "#F9423A", "letter": "💻",
               "featured": False, "added": 35},
    "faz-mcp": {"cat": "news", "color": "#7C2D12", "letter": "🗞️",
               "featured": False, "added": 36},
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
"tagesschau-mcp": {
 "desc_fa": "tagesschau.de (ARD) با فیدهای رسمی RSS (بدون کلید): تیترهای برتر، اخبار بخش‌ها، اخبار منطقه‌ای هر ۱۶ ایالت، جدیدترین ویدیوها و متن کامل مقاله‌ها.",
 "desc_de": "tagesschau.de (ARD) über offizielle RSS-Feeds (kein Schlüssel): Schlagzeilen, Nachrichten nach Ressort, Regionalnachrichten aller 16 Bundesländer, neueste Videos und Volltexte.",
 "tools": {
  "tagesschau_headlines": ("تیترهای برتر tagesschau.de", "Top-Schlagzeilen von tagesschau.de"),
  "tagesschau_news_by_section": ("جدیدترین اخبار یک بخش", "Neueste Nachrichten eines Ressorts"),
  "tagesschau_search_news": ("جست‌وجوی اخبار با کلیدواژه", "Nachrichten nach Stichwort suchen"),
  "tagesschau_get_article": ("متن کامل یک مقاله", "Volltext eines Artikels"),
  "tagesschau_latest_videos": ("جدیدترین ویدیوها", "Neueste Videos"),
  "tagesschau_regional_news": ("اخبار منطقه‌ای یک ایالت", "Regionalnachrichten eines Bundeslandes"),
 }},
"dwd-mcp": {
 "desc_fa": "هواشناسی آلمان از سرویس ملی هواشناسی آلمان (DWD): پیش‌بینی و وضعیت فعلی با مدل ICON از طریق Open-Meteo، هشدارهای رسمی آب‌وهوای DWD و شمارش گرده.",
 "desc_de": "Deutsches Wetter vom Deutschen Wetterdienst (DWD): ICON-Vorhersagen und aktuelles Wetter über Open-Meteo, amtliche Unwetterwarnungen und Pollenflug.",
 "tools": {
  "dwd_forecast": ("پیش‌بینی مدل ICON برای یک شهر آلمان (ساعتی + روزانه)", "ICON-Vorhersage für einen deutschen Ort (stündlich + täglich)"),
  "dwd_current_weather": ("وضعیت فعلی هوا برای یک شهر آلمان", "Aktuelles Wetter für einen deutschen Ort"),
  "dwd_warnings": ("هشدارهای رسمی آب‌وهوای DWD، قابل فیلتر بر اساس ایالت", "Amtliche Unwetterwarnungen des DWD, filterbar nach Bundesland"),
  "dwd_pollen": ("شمارش گرده برای یک شهر آلمان (CAMS از طریق Open-Meteo)", "Pollenflug für einen deutschen Ort (CAMS über Open-Meteo)"),
  "dwd_find_place": ("یافتن شهرهای آلمان (نام → مختصات)", "Deutsche Orte finden (Name → Koordinaten)"),
 }},
"bundeswahlleiter-mcp": {
 "desc_fa": "نتایج رسمی انتخابات بوندستاگ از bundeswahlleiterin.de (داده‌های باز رایگان، بدون کلید): نتایج کشوری، نتایج احزاب، حوزه‌های انتخابیه و میزان مشارکت برای ۲۰۱۷، ۲۰۲۱ و ۲۰۲۵.",
 "desc_de": "Amtliche Bundestagswahlergebnisse von bundeswahlleiterin.de (freie offene Daten, kein Schlüssel, kein Login): Bundesergebnisse, Parteiergebnisse, Wahlkreise und Wahlbeteiligung für 2017, 2021 und 2025.",
 "tools": {
  "bwl_national_results": ("نتایج کشوری یک انتخابات بوندستاگ", "Bundesergebnis einer Bundestagswahl"),
  "bwl_party_results": ("نتایج یک حزب، کشوری و به تفکیک ایالت", "Ergebnis einer Partei, bundesweit und nach Ländern"),
  "bwl_constituency_results": ("نتایج یک حوزهٔ انتخابیه", "Ergebnis eines Wahlkreises"),
  "bwl_constituencies": ("فهرست حوزه‌ها با برنده و میزان مشارکت", "Wahlkreise mit Gewinner und Wahlbeteiligung auflisten"),
  "bwl_turnout": ("میزان مشارکت به تفکیک ایالت و کشوری", "Wahlbeteiligung nach Ländern und bundesweit"),
 }},
"flixtrain-mcp": {
 "desc_fa": "زمان‌بندی و قیمت فلیکس‌ترین از API جست‌وجوی فروشگاه فلیکس‌بوس (رایگان، بدون کلید): فقط سفرهای قطار بین شهرهای آلمان، با ایستگاه‌ها، مدت سفر، قیمت و صندلی‌های موجود.",
 "desc_de": "FlixTrain-Zeiten & Preise über die FlixBus-Shop-Suche (kostenlos, kein Schlüssel, kein Login): nur Zugverbindungen zwischen deutschen Städten, mit Bahnhöfen, Fahrzeit, Preis und Sitzplatzverfügbarkeit.",
 "tools": {
  "flixtrain_search_trains": ("جست‌وجوی سفرهای فلیکس‌ترین بین دو شهر", "FlixTrain-Verbindungen zwischen zwei Städten suchen"),
  "flixtrain_search_cities": ("یافتن شهرها بر اساس نام", "Städte nach Namen finden"),
 }},
"billiger-mcp": {
 "desc_fa": "مقایسهٔ قیمت آلمان از billiger.de (رایگان، بدون کلید): جست‌وجوی محصولات با بهترین قیمت، مقایسهٔ پیشنهادهای فروشگاه‌ها و تخفیف‌های روز.",
 "desc_de": "Deutscher Preisvergleich von billiger.de (kostenlos, kein Schlüssel, kein Login): Produkte mit Bestpreisen suchen, Shop-Angebote vergleichen und Tagesdeals.",
 "tools": {
  "billiger_search_prices": ("جست‌وجوی محصولات با بهترین قیمت", "Produkte mit Bestpreisen suchen"),
  "billiger_product_offers": ("مقایسهٔ پیشنهادهای فروشگاه‌ها برای یک محصول", "Shop-Angebote für ein Produkt vergleichen"),
  "billiger_best_deals": ("تخفیف‌های روز از صفحهٔ اصلی", "Tagesdeals von der Startseite"),
 }},
"fernsehserien-mcp": {
 "desc_fa": "سریال‌های تلویزیونی آلمان از fernsehserien.de (رایگان، بدون کلید): جست‌وجوی سریال، جزئیات سریال، راهنمای قسمت‌ها و زمان‌های پخش آینده.",
 "desc_de": "Deutsche TV-Serien von fernsehserien.de (kostenlos, kein Schlüssel, kein Login): Serien suchen, Seriendetails, Episodenguides und Sendetermine.",
 "tools": {
  "fs_search_series": ("جست‌وجوی سریال‌های تلویزیونی بر اساس نام", "TV-Serien nach Namen suchen"),
  "fs_series_detail": ("جزئیات سریال و فصل‌ها", "Seriendetails und Staffeln"),
  "fs_episodes": ("راهنمای قسمت‌های یک فصل", "Episodenguide einer Staffel"),
  "fs_air_dates": ("زمان‌های پخش آیندهٔ یک سریال", "Kommende Sendetermine einer Serie"),
 }},
"zdf-mcp": {
 "desc_fa": "اخبار ZDF heute از zdfheute.de (رایگان، بدون کلید): تازه‌ترین تیترها، اخبار بر اساس موضوع، جست‌وجوی کلیدواژه و متن کامل مقاله. فقط اخبار — مدیاتک ZDF در این سرور نیست.",
 "desc_de": "ZDF-heute-Nachrichten von zdfheute.de (kostenlos, kein Schlüssel, kein Login): aktuelle Schlagzeilen, Nachrichten nach Thema, Stichwortsuche und Volltext. Nur Nachrichten — keine Mediathek.",
 "tools": {
  "zdf_headlines": ("تازه‌ترین تیترهای ZDF heute", "Aktuelle ZDF-heute-Schlagzeilen"),
  "zdf_news_by_topic": ("اخبار ZDF heute بر اساس موضوع", "ZDF-heute-Nachrichten nach Thema"),
  "zdf_search_news": ("جست‌وجوی تیترهای ZDF heute با کلیدواژه", "ZDF-heute-Schlagzeilen nach Stichwort suchen"),
  "zdf_get_article": ("متن کامل مقالهٔ ZDF heute", "Volltext eines ZDF-heute-Artikels"),
 }},
"ecb-mcp": {
 "desc_fa": "داده‌های بانک مرکزی اروپا از API رسمی SDMX (رایگان، بدون کلید): نرخ‌های ارز یورو، نرخ‌های کلیدی بهره، تورم HICP، عرضهٔ پول M3 و بازده اوراق قرضهٔ منطقهٔ یورو.",
 "desc_de": "Daten der Europäischen Zentralbank über die offizielle SDMX-API (kostenlos, kein Schlüssel, kein Login): Euro-Wechselkurse, EZB-Leitzinsen, HVPI-Inflation, Geldmenge M3 und Anleiherenditen des Euroraums.",
 "tools": {
  "ecb_exchange_rates": ("نرخ‌های ارز یورو در برابر ارزهای اصلی", "Euro-Wechselkurse gegenüber wichtigen Währungen"),
  "ecb_interest_rates": ("نرخ‌های کلیدی بهرهٔ بانک مرکزی اروپا", "EZB-Leitzinsen (Hauptrefinanzierung, Einlage, Spitzenrefinanzierung)"),
  "ecb_inflation": ("تورم HICP منطقهٔ یورو و آلمان", "HVPI-Inflation, Euroraum und Deutschland"),
  "ecb_money_supply": ("عرضهٔ پول منطقهٔ یورو (M1، M2، M3)", "Geldmenge des Euroraums (M1, M2, M3)"),
  "ecb_bond_yields": ("بازده اوراق قرضهٔ دولتی منطقهٔ یورو بر اساس سررسید", "Staatsanleiherenditen des Euroraums nach Laufzeit"),
 }},
"wg-gesucht-mcp": {
 "desc_fa": "آگهی‌های مسکن WG-Gesucht از wg-gesucht.de (رایگان، بدون کلید): اتاق‌های اشتراکی و آپارتمان در ۳۴ شهر آلمانی‌زبان، با قیمت، متراژ، تاریخ در دسترس بودن و جزئیات کامل آگهی.",
 "desc_de": "WG-Gesucht-Angebote von wg-gesucht.de (kostenlos, kein Schlüssel, kein Login): WG-Zimmer und Wohnungen in 34 deutschsprachigen Städten, mit Preis, Größe, Verfügbarkeit und vollständigen Anzeigendetails.",
 "tools": {
  "wg_search_rooms": ("جست‌وجوی اتاق اشتراکی در یک شهر", "WG-Zimmer in einer Stadt suchen"),
  "wg_search_flats": ("جست‌وجوی آپارتمان در یک شهر", "Wohnungen in einer Stadt suchen"),
  "wg_listing_detail": ("جزئیات کامل یک آگهی", "Vollständige Details einer Anzeige"),
  "wg_cities": ("فهرست شهرهای پشتیبانی‌شده", "Unterstützte Städte auflisten"),
 }},
"dictcc-mcp": {
 "desc_fa": "ترجمه‌های dict.cc از dict.cc (رایگان، بدون کلید): آلمانی–انگلیسی و ۲۲ زبان دیگر، با نوع کلمه، جنسیت، توضیحات کاربرد و آرای کاربران.",
 "desc_de": "dict.cc-Übersetzungen von dict.cc (kostenlos, kein Schlüssel, kein Login): Deutsch-Englisch plus 22 weitere Sprachenpaare, mit Wortart, Genus, Gebrauchshinweisen und Community-Stimmen.",
 "tools": {
  "dictcc_translate": ("ترجمهٔ واژه با dict.cc (۲۳ زبان)", "Ein Wort mit dict.cc übersetzen (23 Sprachenpaare)"),
  "dictcc_search": ("یافتن سرخط‌های dict.cc مطابق پرس‌وجو", "dict.cc-Stichwörter zu einer Suchanfrage finden"),
 }},
"duden-mcp": {
 "desc_fa": "جست‌وجو در فرهنگ لغت دودن از duden.de (رایگان، بدون کلید): معانی واژه، مترادف‌ها، املا با جداسازی هجاها، نکات دستوری و صرف کامل فعل.",
 "desc_de": "Duden-Nachschlagen auf duden.de (kostenlos, kein Schlüssel, kein Login): Bedeutungen, Synonyme, Rechtschreibung mit Worttrennung, Grammatik und vollständige Verbkonjugation.",
 "tools": {
  "duden_lookup_word": ("جست‌وجوی واژهٔ آلمانی در دودن: معانی، نوع کلمه و دستور زبان", "Ein deutsches Wort im Duden nachschlagen: Bedeutungen, Wortart & Grammatik"),
  "duden_synonyms": ("مترادف‌های یک واژهٔ آلمانی", "Synonyme eines deutschen Wortes"),
  "duden_spelling": ("املا و جداسازی هجاهای یک واژهٔ آلمانی", "Rechtschreibung & Worttrennung eines deutschen Wortes"),
  "duden_grammar": ("نکات دستوری یک واژهٔ آلمانی", "Grammatiknotizen zu einem deutschen Wort"),
  "duden_conjugate": ("جدول کامل صرف یک فعل آلمانی", "Vollständige Konjugationstabelle eines deutschen Verbs"),
  "duden_search": ("جست‌وجوی سرخط‌های دودن", "Duden-Stichwörter suchen"),
 }},
"deutschlandfunk-mcp": {
 "desc_fa": "اخبار و رادیوی دویچلندفونک از فیدهای RSS رسمی (بدون کلید): اخبار جاری، تازه‌ترین مطالب، فیدهای موضوعی، جست‌وجوی کلیدواژه، متن کامل مقاله و لینک پخش زنده.",
 "desc_de": "Deutschlandfunk-Nachrichten & Radio über die offiziellen RSS-Feeds (kein Schlüssel): laufende Nachrichten, neueste Beiträge, Ressort-Feeds, Stichwortsuche, Volltexte und Livestream-Link.",
 "tools": {
  "dlf_latest_news": ("تیترهای خبری جاری DLF", "Laufende DLF-Nachrichten"),
  "dlf_latest_contributions": ("تازه‌ترین مطالب DLF", "Neueste DLF-Beiträge"),
  "dlf_news_by_topic": ("اخبار DLF بر اساس موضوع", "DLF-Nachrichten nach Ressort"),
  "dlf_search_news": ("جست‌وجوی مطالب اخیر DLF با کلیدواژه", "Neueste DLF-Beiträge nach Stichwort suchen"),
  "dlf_get_article": ("متن کامل یک مقالهٔ DLF", "Volltext eines DLF-Artikels"),
  "dlf_listen_live": ("لینک پخش زندهٔ دویچلندفونک", "Livestream-Link des Deutschlandfunks"),
 }},
"govdata-mcp": {
 "desc_fa": "پورتال ملی داده‌های باز آلمان govdata.de از طریق API رسمی CKAN (بدون کلید): جست‌وجو در بیش از ۱۶۳٬۰۰۰ مجموعه‌داده، جزئیات مجموعه‌داده، ناشران، تازه‌ترین مجموعه‌داده‌ها و جزئیات منبع.",
 "desc_de": "Deutschlands nationales Open-Data-Portal govdata.de über die offizielle CKAN-API (kein Schlüssel): über 163.000 Datensätze durchsuchen, Datensatzdetails, Herausgeber, neueste Datensätze und Ressourcendetails.",
 "tools": {
  "govdata_search_datasets": ("جست‌وجوی مجموعه‌داده‌ها در govdata.de", "Datensätze auf govdata.de suchen"),
  "govdata_get_dataset": ("جزئیات کامل یک مجموعه‌داده", "Vollständige Details eines Datensatzes"),
  "govdata_list_publishers": ("ناشران، به ترتیب بیشترین مجموعه‌داده", "Herausgeber, nach Datensatzzahl sortiert"),
  "govdata_recent_datasets": ("تازه‌ترین مجموعه‌داده‌های به‌روز شده", "Zuletzt aktualisierte Datensätze"),
  "govdata_get_resource": ("جزئیات یک منبع مجموعه‌داده", "Details einer Datensatz-Ressource"),
 }},
"dnb-mcp": {
 "desc_fa": "کاتالوگ کتابخانه ملی آلمان از طریق API رسمی SRU (بدون کلید): جست‌وجوی کلیدواژه، عنوان و نویسنده، جست‌وجو با ISBN و شناسهٔ DNB.",
 "desc_de": "Katalog der Deutschen Nationalbibliothek über die offizielle SRU-API (kein Schlüssel): Stichwort-, Titel- und Autorensuche, ISBN- und DNB-ID-Abfrage.",
 "tools": {
  "dnb_search_books": ("جست‌وجوی کلیدواژه در کاتالوگ DNB", "Stichwortsuche im DNB-Katalog"),
  "dnb_search_by_title": ("جست‌وجو در کاتالوگ DNB با عنوان", "Titelsuche im DNB-Katalog"),
  "dnb_search_by_author": ("جست‌وجو در کاتالوگ DNB با نویسنده", "Autorensuche im DNB-Katalog"),
  "dnb_by_isbn": ("یافتن یک کتاب با ISBN", "Ein Buch per ISBN nachschlagen"),
  "dnb_get_record": ("رکورد کامل با شناسهٔ DNB", "Vollständiger Datensatz per DNB-ID"),
 }},
"ntv-mcp": {
 "desc_fa": "اخبار n-tv از فیدهای RSS رسمی (بدون کلید): تازه‌ترین تیترها بر اساس بخش، اخبار بازار، تازه‌ترین ویدیوها، جست‌وجوی کلیدواژه و متن کامل مقاله.",
 "desc_de": "n-tv-Nachrichten über die offiziellen RSS-Feeds (kein Schlüssel): neueste Schlagzeilen nach Ressort, Börsennachrichten, neueste Videos, Stichwortsuche und Volltexte.",
 "tools": {
  "ntv_headlines": ("تازه‌ترین تیترهای n-tv بر اساس بخش", "Neueste n-tv-Schlagzeilen nach Ressort"),
  "ntv_markets": ("تازه‌ترین اخبار بازار n-tv", "Neueste n-tv-Börsennachrichten"),
  "ntv_videos": ("تازه‌ترین ویدیوهای n-tv", "Neueste n-tv-Videos"),
  "ntv_search_news": ("جست‌وجوی تیترهای اخیر n-tv با کلیدواژه", "Neueste n-tv-Schlagzeilen nach Stichwort suchen"),
  "ntv_get_article": ("متن کامل یک مقالهٔ n-tv", "Volltext eines n-tv-Artikels"),
 }},
"dw-mcp": {
 "desc_fa": "اخبار دویچه‌وله به ۳۱ زبان از سایت‌مپ‌های رسمی DW (بدون کلید): تازه‌ترین تیترها، جست‌وجوی کلیدواژه، تازه‌ترین مقاله‌ها، متن کامل مقاله و صفحه‌های موضوعی.",
 "desc_de": "Deutsche-Welle-Nachrichten in 31 Sprachen über die offiziellen DW-Sitemaps (kein Schlüssel): neueste Schlagzeilen, Stichwortsuche, neueste Artikel, Volltexte und Themenseiten.",
 "tools": {
  "dw_headlines": ("تازه‌ترین تیترهای DW به یک زبان", "Neueste DW-Schlagzeilen in einer Sprache"),
  "dw_search_news": ("جست‌وجوی تیترهای اخیر DW با کلیدواژه", "Neueste DW-Schlagzeilen nach Stichwort suchen"),
  "dw_latest_articles": ("تازه‌ترین مقاله‌های DW به یک زبان", "Neueste DW-Artikel in einer Sprache"),
  "dw_get_article": ("متن کامل یک مقالهٔ DW", "Volltext eines DW-Artikels"),
  "dw_topics": ("صفحه‌های موضوعی DW برای یک واژه", "DW-Themenseiten zu einem Stichwort"),
 }},
"autobahn-mcp": {
 "desc_fa": "داده‌های اتوبان آلمان از API رسمی verkehr.autobahn.de (بدون کلید): کارهای جاده‌ای، بسته‌شدن‌ها، هشدارها، پارکینگ کامیون/خودرو و ایستگاه‌های شارژ خودروی برقی برای هر اتوبان.",
 "desc_de": "Deutsche Autobahn-Daten über die offizielle API verkehr.autobahn.de (kein Schlüssel): Baustellen, Sperrungen, Warnungen, LKW-/PKW-Parkplätze und E-Ladesäulen je Autobahn.",
 "tools": {
  "autobahn_roadworks": ("کارهای جاده‌ای یک اتوبان", "Baustellen auf einer Autobahn"),
  "autobahn_closures": ("بسته‌شدن‌های یک اتوبان", "Sperrungen auf einer Autobahn"),
  "autobahn_warnings": ("هشدارهای یک اتوبان", "Warnungen auf einer Autobahn"),
  "autobahn_parking": ("پارکینگ‌های یک اتوبان", "Parkplätze auf einer Autobahn"),
  "autobahn_ev_charging": ("ایستگاه‌های شارژ خودروی برقی یک اتوبان", "E-Ladesäulen auf einer Autobahn"),
 }},
"uba-mcp": {
 "desc_fa": "کیفیت هوای آلمان از API نسخهٔ ۴ داده‌های هوای UBA (بدون کلید): اندازه‌گیری‌های ساعتی از بیش از ۴۰۰ ایستگاه آلمان، آلاینده‌ها، شاخص LQI و شبکه‌های اندازه‌گیری.",
 "desc_de": "Deutsche Luftqualität über die UBA Air Data API v4 (kein Schlüssel): stündliche Messwerte von über 400 deutschen Stationen, Schadstoffe, LQI-Klassen und Messnetze.",
 "tools": {
  "uba_list_stations": ("ایستگاه‌های اندازه‌گیری، قابل فیلتر بر اساس شهر، ایالت، نوع، منطقه یا نام", "Messstationen, filterbar nach Stadt, Bundesland, Typ, Gebiet oder Name"),
  "uba_station_detail": ("جزئیات یک ایستگاه: آدرس، مختصات، نوع، بازهٔ داده‌ها، آلاینده‌های اخیر", "Details einer Station: Adresse, Koordinaten, Typ, Datenzeitraum, aktuelle Schadstoffe"),
  "uba_current_air_quality": ("آخرین مقادیر ساعتی + شاخص LQI در یک ایستگاه", "Aktuelle Stundenwerte + LQI an einer Station"),
  "uba_measurements": ("مقادیر ساعتی در یک بازه + کمینه/بیشینه/میانگین و میانگین روزانه", "Stundenwerte über einen Zeitraum + Min/Max/Mittel & Tagesmittel"),
  "uba_list_components": ("هر ۱۲ آلاینده: کد، نماد، واحد، نام", "Alle 12 Schadstoffe: Code, Symbol, Einheit, Name"),
  "uba_list_networks": ("شبکه‌های اندازه‌گیری (۱۶ ایالت + UBA)", "Die Messnetze (16 Bundesländer + UBA)"),
 }},
"openplz-mcp": {
 "desc_fa": "داده‌های پستی آلمان از OpenPLZ API (بدون کلید): کد پستی، شهرها، خیابان‌ها، شهرداری‌ها، بخش‌ها و ۱۶ ایالت فدرال.",
 "desc_de": "Deutsche Postdaten über die OpenPLZ API (kein Schlüssel): Postleitzahlen, Orte, Straßen, Gemeinden, Kreise und die 16 Bundesländer.",
 "tools": {
  "openplz_lookup_postal_code": ("کدام شهر (یا شهرها) متعلق به یک کد پستی است", "Zu welchem Ort (oder welchen Orten) eine Postleitzahl gehört"),
  "openplz_search_locality": ("جست‌وجوی شهرها بر اساس نام، اختیاری درون یک کد پستی", "Orte nach Namen suchen, optional innerhalb einer Postleitzahl"),
  "openplz_search_street": ("جست‌وجوی خیابان‌ها بر اساس نام، کد پستی و/یا شهر", "Straßen nach Name, Postleitzahl und/oder Ort suchen"),
  "openplz_full_text_search": ("جست‌وجوی آزاد در نام خیابان، کد پستی و شهر", "Freitextsuche über Straßenname, Postleitzahl und Stadt"),
  "openplz_list_federal_states": ("هر ۱۶ ایالت فدرال با کد + مرکز", "Alle 16 Bundesländer mit Schlüssel + Hauptstadt"),
  "openplz_admin_children": ("یک قدم پایین‌تر در درخت اداری (ایالت ← بخش ← شهرداری)", "Einen Schritt im Verwaltungsbaum nach unten (Land → Kreis → Gemeinde)"),
 }},
"feiertage-mcp": {
 "desc_fa": "تعطیلات رسمی آلمان از feiertage-api.de (API رایگان، بدون کلید): تعطیلات هر سال در هر ایالت فدرال، بررسی تعطیل بودن یک تاریخ، نزدیک‌ترین تعطیل و تعطیلات در یک بازه.",
 "desc_de": "Deutsche Feiertage über feiertage-api.de (kostenlose API, kein Schlüssel): Feiertage pro Jahr und Bundesland, Ist-es-ein-Feiertag-Prüfung, nächster Feiertag und Feiertage in einem Zeitraum.",
 "tools": {
  "feiertage_list_holidays": ("تعطیلات رسمی یک سال در یک ایالت فدرال (با فیلتر اختیاری ماه)", "Feiertage eines Jahres in einem Bundesland (optional nach Monat gefiltert)"),
  "feiertage_is_holiday": ("آیا یک تاریخ در یک ایالت تعطیل رسمی است؟", "Ist ein Datum ein Feiertag in einem Bundesland?"),
  "feiertage_next_holiday": ("نزدیک‌ترین تعطیل رسمی از یک تاریخ به بعد", "Der nächste Feiertag ab einem Datum"),
  "feiertage_holidays_between": ("تعطیلات رسمی در یک بازهٔ زمانی (حداکثر حدود ۲ سال)", "Feiertage in einem Zeitraum (max. ca. 2 Jahre)"),
  "feiertage_list_states": ("هر ۱۶ ایالت فدرال + NATIONAL (تعطیلات سراسری)", "Alle 16 Bundesländer + NATIONAL (bundesweite Feiertage)"),
 }},
"ferien-mcp": {
 "desc_fa": "تعطیلات مدارس آلمان از ferien-api.de (API رایگان، بدون کلید): تعطیلات هر سال در هر ایالت فدرال، بررسی اینکه یک تاریخ در تعطیلات مدارس است یا نه، نزدیک‌ترین تعطیلات و تعطیلات در یک بازه.",
 "desc_de": "Deutsche Schulferien über ferien-api.de (kostenlose API, kein Schlüssel): Ferien pro Jahr und Bundesland, Ist-es-ein-Ferientag-Prüfung, nächste Ferien und Ferien in einem Zeitraum.",
 "tools": {
  "ferien_list_holidays": ("تعطیلات مدارس یک سال در یک ایالت فدرال (با فیلتر اختیاری ماه)", "Schulferien eines Jahres in einem Bundesland (optional nach Monat gefiltert)"),
  "ferien_is_holiday": ("آیا یک تاریخ در تعطیلات مدارس یک ایالت است؟", "Liegt ein Datum in den Schulferien eines Bundeslandes?"),
  "ferien_next_holiday": ("نزدیک‌ترین تعطیلات مدارس از یک تاریخ به بعد", "Die nächsten Schulferien ab einem Datum"),
  "ferien_holidays_between": ("تعطیلات مدارس در یک بازهٔ زمانی (حداکثر حدود ۲ سال)", "Schulferien in einem Zeitraum (max. ca. 2 Jahre)"),
  "ferien_list_states": ("هر ۱۶ ایالت فدرال", "Alle 16 Bundesländer"),
 }},
"spiegel-mcp": {
 "desc_fa": "اخبار اشپیگل از spiegel.de (فیدهای رسمی RSS، بدون کلید): تیترهای برتر، اخبار ۱۳ بخش، جست‌وجوی کلیدواژه، جدیدترین ویدیوها و متن مقاله‌ها (مقاله‌های پولی SPIEGEL+ صادقانه مشخص می‌شوند).",
 "desc_de": "DER SPIEGEL über spiegel.de (offizielle RSS-Feeds, kein Schlüssel): Top-Schlagzeilen, 13 Ressorts, Stichwortsuche, neueste Videos und Artikeltexte (SPIEGEL+-Artikel werden ehrlich gekennzeichnet).",
 "tools": {
  "spiegel_headlines": ("تیترهای برتر (Schlagzeilen)، جدیدترین اول", "Top-Schlagzeilen, neueste zuerst"),
  "spiegel_news_by_section": ("جدیدترین اخبار یکی از ۱۳ بخش", "Neueste Nachrichten eines von 13 Ressorts"),
  "spiegel_search_news": ("جست‌وجوی اخبار با کلیدواژه در همهٔ فیدها", "Nachrichtensuche nach Stichwort über alle Feeds"),
  "spiegel_get_article": ("متن یک مقالهٔ spiegel.de (پولی بودن مشخص می‌شود)", "Artikeltext eines spiegel.de-Artikels (Paywall wird gekennzeichnet)"),
  "spiegel_latest_videos": ("جدیدترین ویدیوهای اشپیگل، جدیدترین اول", "Neueste SPIEGEL-Videos, neueste zuerst"),
 }},
"heise-mcp": {
 "desc_fa": "اخبار فناوری اطلاعات هایزه از heise.de (فید رسمی RSS، بدون کلید): تیترهای برتر، اخبار ۷ بخش، جست‌وجوی کلیدواژه، خبرهای برتر صفحهٔ اصلی، مقاله‌های مجلهٔ c't و متن مقاله‌ها (مقاله‌های پولی heise+ صادقانه مشخص می‌شوند).",
 "desc_de": "heise online über heise.de (offizieller RSS-Feed, kein Schlüssel): Top-Schlagzeilen, 7 Ressorts, Stichwortsuche, Top-Meldungen der Startseite, c't-Artikel und Artikeltexte (heise+-Artikel werden ehrlich gekennzeichnet).",
 "tools": {
  "heise_headlines": ("تیترهای برتر (فید اصلی RSS)، جدیدترین اول", "Top-Schlagzeilen (Haupt-RSS-Feed), neueste zuerst"),
  "heise_search_news": ("جست‌وجوی اخبار با کلیدواژه در فید اصلی", "Nachrichtensuche nach Stichwort im Haupt-Feed"),
  "heise_news_by_section": ("جدیدترین اخبار یکی از ۷ بخش", "Neueste Nachrichten eines von 7 Ressorts"),
  "heise_top_stories": ("خبرهای برتر صفحهٔ اصلی، به ترتیب صفحه", "Top-Meldungen der Startseite, in Seitenreihenfolge"),
  "heise_ct": ("جدیدترین مقاله‌های مجلهٔ c't", "Neueste Artikel aus der c't"),
  "heise_get_article": ("متن یک مقالهٔ heise.de (پولی بودن مشخص می‌شود)", "Artikeltext eines heise.de-Artikels (Paywall wird gekennzeichnet)"),
 }},
"zeit-mcp": {
 "desc_fa": "اخبار روزنامهٔ تسایت (DIE ZEIT) از فیدهای رسمی RSS (بدون کلید): تیترهای برتر، اخبار ۱۰ بخش، جست‌وجوی کلیدواژه در فید اصلی و همهٔ بخش‌ها، و فهرست بخش‌ها.",
 "desc_de": "DIE ZEIT über die offiziellen RSS-Feeds (kein Schlüssel): Top-Schlagzeilen, Nachrichten aus 10 Ressorts, Stichwortsuche im Haupt-Feed und über alle Ressorts sowie die Ressortliste.",
 "tools": {
  "zeit_headlines": ("تیترهای برتر (فید اصلی RSS)، جدیدترین اول", "Top-Schlagzeilen (Haupt-RSS-Feed), neueste zuerst"),
  "zeit_news_by_section": ("جدیدترین اخبار یکی از ۱۰ بخش", "Neueste Nachrichten eines von 10 Ressorts"),
  "zeit_search_news": ("جست‌وجوی اخبار با کلیدواژه در فید اصلی", "Nachrichtensuche nach Stichwort im Haupt-Feed"),
  "zeit_search_all_sections": ("جست‌وجوی اخبار با کلیدواژه در همهٔ فیدهای بخش‌ها", "Nachrichtensuche nach Stichwort über alle Ressort-Feeds"),
  "zeit_sections": ("فهرست ۱۰ بخش دارای فید RSS", "Liste der 10 Ressorts mit RSS-Feed"),
 }},
"welt-mcp": {
 "desc_fa": "اخبار روزنامهٔ ولت (WELT) از فید رسمی RSS و صفحات مقالات (بدون کلید): تیترهای برتر، اخبار بر اساس موضوع، جست‌وجوی کلیدواژه، جدیدترین ویدیوها و متن کامل مقاله‌ها (مقاله‌های پولی WELT+ صادقانه مشخص می‌شوند).",
 "desc_de": "WELT über den offiziellen RSS-Feed und Artikelseiten (kein Schlüssel): Top-Schlagzeilen, Nachrichten nach Thema, Stichwortsuche, neueste Videos und Artikeltexte (WELT+-Artikel werden ehrlich gekennzeichnet).",
 "tools": {
  "welt_headlines": ("تیترهای برتر (فید رسمی RSS)، جدیدترین اول", "Top-Schlagzeilen (offizieller RSS-Feed), neueste zuerst"),
  "welt_news_by_topic": ("جدیدترین اخبار یک موضوع (آلمان، خارج، فوتبال، فرهنگ و …)", "Neueste Nachrichten zu einem Thema (Deutschland, Ausland, Fußball, Kultur, …)"),
  "welt_search_news": ("جست‌وجوی اخبار با کلیدواژه در فید", "Nachrichtensuche nach Stichwort im Feed"),
  "welt_latest_videos": ("جدیدترین ویدیوهای ولت، جدیدترین اول", "Neueste WELT-Videos, neueste zuerst"),
  "welt_get_article": ("متن یک مقالهٔ welt.de (پولی بودن مشخص می‌شود)", "Artikeltext eines welt.de-Artikels (Paywall wird gekennzeichnet)"),
 }},
"ndr-mcp": {
 "desc_fa": "اخبار NDR، رسانهٔ عمومی شمال آلمان، از فیدهای رسمی RSS (بدون کلید): تیترهای برتر، اخبار منطقه‌ای چهار ایالت، اخبار بر اساس بخش، جست‌وجوی کلیدواژه و متن کامل مقالات (بخش kultur از طریق SSR، صفحات ویدیویی مشخص می‌شوند).",
 "desc_de": "NDR über die offiziellen RSS-Feeds (kein Schlüssel): Top-Schlagzeilen, Regionalnachrichten für die vier Länder, Nachrichten nach Ressort, Stichwortsuche und Artikeltexte (kultur per SSR, Videoseiten werden gekennzeichnet).",
 "tools": {
  "ndr_headlines": ("تیترهای برتر (فید رسمی RSS)، جدیدترین اول", "Top-Schlagzeilen (offizieller RSS-Feed), neueste zuerst"),
  "ndr_news_by_region": ("تازه‌ترین اخبار یکی از چهار ایالت پخش", "Neueste Nachrichten aus einem der vier Sendeländer"),
  "ndr_news_by_section": ("تازه‌ترین اخبار یک بخش (اخبار، فرهنگ، ورزش و …)", "Neueste Nachrichten eines Ressorts (nachrichten, kultur, sport, …)"),
  "ndr_search_news": ("جست‌وجوی اخبار با کلیدواژه در فید اصلی", "Nachrichtensuche nach Stichwort im Haupt-Feed"),
  "ndr_get_article": ("متن یک مقالهٔ ndr.de (JSON-LD یا SSR؛ ویدیویی بودن مشخص می‌شود)", "Artikeltext eines ndr.de-Artikels (JSON-LD oder SSR; Video wird gekennzeichnet)"),
 }},
"br-mcp": {
 "desc_fa": "اخبار BR، رسانهٔ عمومی بایرن، از فیدهای رسمی RSS (بدون کلید): تیکر خبری BR24، اخبار بر اساس دسته (بایرن، دانش، ورزش، فرهنگ، اقتصاد)، جست‌وجوی کلیدواژه، متن کامل مقالات، مطالب رادیویی Bayern 1 و Bayern 2 و گزارش‌های ترافیک.",
 "desc_de": "BR über die offiziellen RSS-Feeds (kein Schlüssel): BR24-Ticker, Nachrichten nach Kategorie (Bayern, Wissen, Sport, Kultur, Wirtschaft), Stichwortsuche, Artikeltexte, Bayern-1-/Bayern-2-Geschichten und Verkehrsmeldungen.",
 "tools": {
  "br_headlines": ("تیترهای برتر تیکر BR24 (فید رسمی RSS)، جدیدترین اول", "Top-Meldungen des BR24-Tickers (offizieller RSS-Feed), neueste zuerst"),
  "br_news_by_category": ("تازه‌ترین اخبار یک دسته (بایرن، دانش، ورزش، فرهنگ، اقتصاد)", "Neueste Nachrichten einer Kategorie (bayern, wissen, sport, kultur, wirtschaft)"),
  "br_search_news": ("جست‌وجوی اخبار با کلیدواژه در تیکر و فیدهای دسته", "Nachrichtensuche nach Stichwort über Ticker und Kategorien-Feeds"),
  "br_get_article": ("متن کامل یک مقالهٔ br.de (پاراگراف‌های <article> رندرشده در سرور)", "Volltext eines br.de-Artikels (serverseitig gerenderte <article>-Absätze)"),
  "br_radio": ("تازه‌ترین مطالب یک ایستگاه رادیویی BR (bayern1 یا bayern2)", "Neueste Geschichten eines BR-Radiosenders (bayern1 oder bayern2)"),
  "br_traffic": ("گزارش‌های جاری ترافیک BR", "Aktuelle Verkehrsmeldungen des BR"),
 }},
"focus-online-mcp": {
 "desc_fa": "اخبار FOCUS online، یکی از بزرگ‌ترین مجله‌های خبری آلمان، از فید رسمی RSS (بدون کلید): تیترهای برتر، اخبار بر اساس بخش، فهرست بخش‌ها، جست‌وجوی کلیدواژه و متن کامل مقالات (لایوتیکرها مشخص می‌شوند).",
 "desc_de": "FOCUS online, eines der größten Nachrichtenmagazine Deutschlands, über den offiziellen RSS-Feed (kein Schlüssel): Top-Schlagzeilen, Nachrichten nach Ressort, Ressort-Übersicht, Stichwortsuche und Artikeltexte (Live-Ticker werden gekennzeichnet).",
 "tools": {
  "focus_headlines": ("تیترهای برتر (فید رسمی RSS با حدود ۴۰۰ مورد)، جدیدترین اول", "Top-Schlagzeilen (offizieller RSS-Feed, ~400 Einträge), neueste zuerst"),
  "focus_news_by_section": ("تازه‌ترین اخبار یک بخش (سیاست، فرهنگ، ورزش، اقتصاد و …)", "Neueste Nachrichten eines Ressorts (politik, kultur, sport, finanzen, …)"),
  "focus_sections": ("بخش‌های فید امروز با تعداد موارد هرکدام", "Ressorts im heutigen Feed mit ihren Eintragszahlen"),
  "focus_search_news": ("جست‌وجوی اخبار با کلیدواژه در کل فید رسمی", "Nachrichtensuche nach Stichwort im gesamten offiziellen RSS-Feed"),
  "focus_get_article": ("متن کامل یک مقالهٔ focus.de (پاراگراف‌های <article> رندرشده در سرور؛ لایوتیکر مشخص می‌شود)", "Volltext eines focus.de-Artikels (serverseitig gerenderte <article>-Absätze; Live-Ticker wird gekennzeichnet)"),
  "focus_health": ("بررسی دسترسی به فید RSS", "Erreichbarkeitsprüfung des RSS-Feeds"),
 }},
"bundesregierung-mcp": {
 "desc_fa": "وب‌سایت رسمی دولت فدرال آلمان (بدون کلید): جدیدترین بیانیه‌های مطبوعاتی، مقاله‌ها، سخنرانی‌ها و کنفرانس‌های مطبوعاتی، جست‌وجوی کلیدواژه و متن کامل اسناد (با ترجمهٔ رسمی انگلیسی در صورت وجود).",
 "desc_de": "Die offizielle Website der Bundesregierung (kein Schlüssel): neueste Pressemitteilungen, Artikel, Reden und Pressekonferenzen, Stichwortsuche und Volltexte (mit offizieller englischer Übersetzung, sofern vorhanden).",
 "tools": {
  "breg_press_releases": ("جدیدترین بیانیه‌های مطبوعاتی دولت فدرال آلمان، جدیدترین اول", "Neueste Pressemitteilungen der Bundesregierung, neueste zuerst"),
  "breg_articles": ("جدیدترین مقاله‌ها / Meldungen از bundesregierung.de، جدیدترین اول", "Neueste Artikel / Meldungen von bundesregierung.de, neueste zuerst"),
  "breg_speeches": ("جدیدترین سخنرانی‌ها، بیانیه‌ها و کنفرانس‌های مطبوعاتی (بیشتر رونوشت کامل)", "Neueste Reden, Pressestatements und Pressekonferenzen (meist vollständige Mitschriften)"),
  "breg_search": ("جست‌وجوی کلیدواژه در کل سایت bundesregierung.de", "Stichwortsuche auf der gesamten Website bundesregierung.de"),
  "breg_get_document": ("متن کامل یک بیانیه، مقاله یا سخنرانی (با ترجمهٔ رسمی انگلیسی در صورت وجود)", "Volltext einer Pressemitteilung, eines Artikels oder einer Rede (mit offizieller englischer Übersetzung, sofern vorhanden)"),
  "breg_health": ("بررسی دسترس‌پذیری فهرست بیانیه‌های مطبوعاتی", "Erreichbarkeits-Check der Pressemitteilungs-Liste"),
 }},
"mdr-mcp": {
 "desc_fa": "MDR — رادیو-تلویزیون آلمان مرکزی، رسانهٔ عمومی زاکسن، زاکسن-آنهالت و تورینگن (بدون کلید): تیترهای برتر، اخبار بر اساس ایالت، شهر و بخش، جست‌وجوی کلیدواژه و متن کامل مقالات (لایوتیکرها مشخص می‌شوند).",
 "desc_de": "MDR — Mitteldeutscher Rundfunk, öffentlich-rechtlicher Sender für Sachsen, Sachsen-Anhalt und Thüringen (kein Schlüssel): Top-Schlagzeilen, Nachrichten nach Bundesland, Stadt und Ressort, Stichwortsuche und Artikeltexte (Live-Ticker werden gekennzeichnet).",
 "tools": {
  "mdr_headlines": ("تیترهای برتر MDR Aktuell، جدیدترین اول", "Top-Schlagzeilen von MDR Aktuell, neueste zuerst"),
  "mdr_regional_news": ("تازه‌ترین اخبار MDR برای یک ایالت فدرال (زاکسن، زاکسن-آنهالت، تورینگن)", "Neueste MDR-Nachrichten eines Bundeslands (Sachsen, Sachsen-Anhalt, Thüringen)"),
  "mdr_local_news": ("تازه‌ترین اخبار MDR برای یک شهر (لایپزیگ، درسدن، کمنیتس، ماگدبورگ، هاله)", "Neueste MDR-Nachrichten einer Stadt (Leipzig, Dresden, Chemnitz, Magdeburg, Halle)"),
  "mdr_section_news": ("تازه‌ترین اخبار MDR در یک بخش (آلمان، فرهنگ، دانش، ورزش)", "Neueste MDR-Nachrichten eines Ressorts (Deutschland, Kultur, Wissen, Sport)"),
  "mdr_search_news": ("جست‌وجوی اخبار MDR با کلیدواژه در همهٔ فیدها", "Nachrichtensuche nach Stichwort in allen MDR-Feeds"),
  "mdr_get_article": ("متن کامل یک مقالهٔ MDR (لایوتیکر مشخص می‌شود)", "Volltext eines MDR-Artikels (Live-Ticker wird gekennzeichnet)"),
 }},
"bild-mcp": {
 "desc_fa": "BILD — بزرگ‌ترین روزنامهٔ زرد و برند خبری دیجیتال آلمان (بدون کلید): تیترهای برتر، اخبار هر بخش، جست‌وجوی کلیدواژه، داستان‌های ویدیویی، داستان‌های BILDplus و متن کامل مقالات (BILDplus با پرچم پولی مشخص می‌شود).",
 "desc_de": "BILD — Deutschlands größte Boulevardzeitung und digitale Nachrichtenmarke (kein Schlüssel): Top-Schlagzeilen, Nachrichten nach Ressort, Stichwortsuche, Video-Geschichten, BILDplus-Geschichten und Artikeltexte (BILDplus wird als Paywall gekennzeichnet).",
 "tools": {
  "bild_headlines": ("تیترهای برتر BILD، جدیدترین اول", "Top-Schlagzeilen von BILD, neueste zuerst"),
  "bild_section_news": ("تازه‌ترین اخبار BILD در یک بخش (سیاست، ورزش، سرگرمی، دیجیتال، خودرو، سفر، پول)", "Neueste BILD-Nachrichten eines Ressorts (Politik, Sport, Unterhaltung, Digital, Auto, Reise, Geld)"),
  "bild_search_news": ("جست‌وجوی اخبار BILD با کلیدواژه در همهٔ فیدها", "Nachrichtensuche nach Stichwort in allen BILD-Feeds"),
  "bild_videos": ("تازه‌ترین داستان‌های BILD با ویدیوی داخلی", "Neueste BILD-Geschichten mit eingebettetem Video"),
  "bild_premium_news": ("تازه‌ترین داستان‌های BILDplus (پشت پی‌وال)", "Neueste BILDplus-Geschichten (hinter der Paywall)"),
  "bild_get_article": ("متن کامل یک مقالهٔ BILD (BILDplus با پرچم پولی مشخص می‌شود)", "Volltext eines BILD-Artikels (BILDplus wird als Paywall gekennzeichnet)"),
 }},
"taz-mcp": {
 "desc_fa": "taz — دی تاگس‌تسایتونگ، روزنامهٔ سراسری چپ‌میانهٔ آلمان (بدون کلید): تیترهای برتر، جست‌وجوی کلیدواژه، مقاله‌ها بر اساس نویسنده، نویسندگان فید امروز و متن کامل مقالات (بخش از breadcrumb صفحه).",
 "desc_de": "taz — die tageszeitung, Deutschlands linksliberale überregionale Tageszeitung (kein Schlüssel): Top-Schlagzeilen, Stichwortsuche, Artikel nach Autor:in, Autor:innen des heutigen Feeds und Artikeltexte (Ressort aus den Breadcrumbs).",
 "tools": {
  "taz_headlines": ("تیترهای برتر taz، جدیدترین اول", "Top-Schlagzeilen der taz, neueste zuerst"),
  "taz_search_news": ("جست‌وجوی اخبار taz با کلیدواژه در فید", "Nachrichtensuche nach Stichwort im Feed"),
  "taz_by_author": ("تازه‌ترین مقاله‌های taz از یک نویسنده", "Neueste taz-Artikel einer Autorin / eines Autors"),
  "taz_authors": ("نویسندگان فید امروز taz با تعداد مقاله‌ها", "Autor:innen des heutigen taz-Feeds mit Artikelzahlen"),
  "taz_get_article": ("متن کامل یک مقالهٔ taz (بخش از breadcrumb صفحه)", "Volltext eines taz-Artikels (Ressort aus den Breadcrumbs)"),
 }},
"t3n-mcp": {
 "desc_fa": "t3n — مجلهٔ فناوری شناخته‌شدهٔ آلمان (بدون کلید): تازه‌ترین اخبار، جست‌وجوی کلیدواژه، مقاله‌ها بر اساس برچسب موضوعی، موضوع‌های فیدهای امروز و متن کامل مقالات (بخش از articleSection صفحه).",
 "desc_de": "t3n — Deutschlands bekanntes Tech-Magazin (kein Schlüssel): neueste Meldungen, Stichwortsuche, Artikel nach Themen-Tag, Themen der heutigen Feeds und Artikeltexte (Ressort aus der articleSection).",
 "tools": {
  "t3n_latest": ("تازه‌ترین اخبار t3n، جدیدترین اول", "Neueste t3n-Meldungen, neueste zuerst"),
  "t3n_search_news": ("جست‌وجوی اخبار t3n با کلیدواژه در هر دو فید", "Nachrichtensuche nach Stichwort in beiden t3n-Feeds"),
  "t3n_by_topic": ("تازه‌ترین مقاله‌های t3n درباره یک برچسب موضوعی", "Neueste t3n-Artikel zu einem Themen-Tag"),
  "t3n_topics": ("برچسب‌های موضوعی فیدهای امروز t3n با تعداد مقاله‌ها", "Themen-Tags der heutigen t3n-Feeds mit Artikelzahlen"),
  "t3n_get_article": ("متن کامل یک مقالهٔ t3n (بخش از articleSection صفحه)", "Volltext eines t3n-Artikels (Ressort aus der articleSection)"),
 }},
"faz-mcp": {
 "desc_fa": "FAZ — فرانکفورتر آلگماینه تسایتونگ، یکی از بزرگ‌ترین روزنامه‌های کیفی آلمان (بدون کلید): تازه‌ترین اخبار، جست‌وجوی کلیدواژه، مقاله‌ها بر اساس بخش و نویسنده، بخش‌های فید امروز و متن کامل مقالات (FAZ+ با پرچم پولی مشخص می‌شود).",
 "desc_de": "FAZ — Frankfurter Allgemeine Zeitung, eine der größten deutschen Qualitätszeitungen (kein Schlüssel): neueste Meldungen, Stichwortsuche, Artikel nach Ressort und Autor:in, Ressorts des heutigen Feeds und Artikeltexte (FAZ+ wird als Paywall gekennzeichnet).",
 "tools": {
  "faz_latest": ("تازه‌ترین اخبار FAZ، جدیدترین اول", "Neueste FAZ-Meldungen, neueste zuerst"),
  "faz_search_news": ("جست‌وجوی اخبار FAZ با کلیدواژه در فید اصلی", "Nachrichtensuche nach Stichwort im FAZ-Hauptfeed"),
  "faz_by_section": ("تازه‌ترین مقاله‌های FAZ از یک فید بخش", "Neueste FAZ-Artikel eines Ressort-Feeds"),
  "faz_sections": ("بخش‌های فید اصلی امروز FAZ با تعداد مقاله‌ها", "Ressorts des heutigen FAZ-Hauptfeeds mit Artikelzahlen"),
  "faz_by_author": ("تازه‌ترین مقاله‌های FAZ از یک نویسنده", "Neueste FAZ-Artikel einer Autorin / eines Autors"),
  "faz_get_article": ("متن کامل یک مقالهٔ FAZ (FAZ+ با پرچم پولی مشخص می‌شود)", "Volltext eines FAZ-Artikels (FAZ+ wird als Paywall gekennzeichnet)"),
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


def write_agent_files(order):
    """Regenerate .mcp.json + llms.txt + llms-full.txt + catalog.json +
    search.json + sitemap.xml + robots.txt at the project root (pushed to
    the catalog repo root so Pages serves them; the Connect page links
    llms.txt, the footer links catalog.json/search.json, the palette
    fetches search.json).
    NOTE: the factory cron must push these files after each regen —
    update_platform.py only writes them locally."""
    servers = [BY_ID[n] for n in order]
    today = datetime.date.today().isoformat()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    site = "https://mohammad-abbasi-sh.github.io/germany-mcp"
    mcp = {"mcpServers": {
        s["name"].replace("-mcp", ""): {"command": "uvx", "args": [s["pypi"]]}
        for s in servers}}
    (HERE / ".mcp.json").write_text(
        json.dumps(mcp, indent=2, ensure_ascii=False) + "\n")
    n_tools = sum(len(s["tools"]) for s in servers)
    # --- llms.txt (with detail-page links + data files) ---
    lines = [
        "# Germany MCP",
        "",
        "> %d read-only MCP servers (%d tools) for German web services — "
        "news, weather, transport, open data, finance, housing, sports and "
        "more. Every server runs locally with uvx, no API key, no account."
        % (len(servers), n_tools),
        "",
        "## Servers",
        "",
    ]
    for s in servers:
        lines.append("- [%s](%s): %s (%d tools) — details + Markdown version: %s/#/en/tool/%s" % (
            s["name"], s["repository"], s["description"], len(s["tools"]), site, s["name"]))
    lines += [
        "",
        "## Data files",
        "",
        "- Full catalog JSON: %s/catalog.json" % site,
        "- Search index: %s/search.json" % site,
        "- Full catalog text: %s/llms-full.txt" % site,
        "",
        "## Install",
        "",
        "- Claude Code: `claude mcp add --transport stdio --scope user "
        "<name> -- uvx <package>`",
        "- Any MCP client: add `{\"command\": \"uvx\", \"args\": "
        "[\"<package>\"]}` under `mcpServers` in the client's config.",
        "- All servers at once: clone "
        "https://github.com/mohammad-abbasi-sh/germany-mcp and open it in "
        "Claude Code — `.mcp.json` registers every server.",
        "- Profile builder (pick servers, get a ready config): "
        "%s/#/en/builder" % site,
        "",
        "## Links",
        "",
        "- Catalog: %s/" % site,
        "- Ask (find the right server): %s/#/ask/" % site,
        "- GitHub: https://github.com/mohammad-abbasi-sh/germany-mcp",
        "",
    ]
    (HERE / "llms.txt").write_text("\n".join(lines))
    # --- llms-full.txt: full catalog text in one file ---
    full = [
        "# Germany MCP — full catalog",
        "",
        "Generated %s. %d read-only MCP servers (%d tools) for German web "
        "services. Every server runs locally with uvx, no API key, no "
        "account." % (now, len(servers), n_tools),
        "",
    ]
    for s in servers:
        meta = SERVER_META[s["name"]]
        full += ["## %s" % s["name"], "", s["description"], "",
                 "- Category: %s" % meta["cat"],
                 "- Repository: %s" % s["repository"],
                 "- PyPI: https://pypi.org/project/%s/" % s["pypi"],
                 "- Install: `claude mcp add --transport stdio --scope user %s -- uvx %s`" % (s["name"].replace("-mcp", ""), s["pypi"]),
                 "- Tools (%d):" % len(s["tools"]), ""]
        for t in s["tools"]:
            full.append("  - `%s`: %s" % (t["name"], t["summary"]))
        full.append("")
    (HERE / "llms-full.txt").write_text("\n".join(full))
    # --- catalog.json: public machine-readable catalog ---
    catalog = {
        "catalog": "germany-mcp",
        "generatedAt": now,
        "count": {"servers": len(servers), "tools": n_tools},
        "servers": [],
    }
    for s in servers:
        meta = SERVER_META[s["name"]]
        tr = TRANSLATIONS[s["name"]]
        catalog["servers"].append({
            "id": s["name"],
            "name": s["name"],
            "summary": s["description"],
            "summary_fa": tr["desc_fa"],
            "summary_de": tr["desc_de"],
            "category": meta["cat"],
            "tags": [meta["cat"], "read-only", "uvx", "no-api-key"],
            "source": "germany-mcp",
            "featured": bool(meta["featured"]),
            "added": meta["added"],
            "health": "verified",
            "lastChecked": today,
            "repo": s["repository"],
            "pypi": s["pypi"],
            "url": "%s/#/en/tool/%s" % (site, s["name"]),
            "install": {"transport": "stdio", "command": "uvx",
                        "args": [s["pypi"]]},
            "tools": [{"name": t["name"], "summary": t["summary"],
                       "summary_fa": tr["tools"][t["name"]][0],
                       "summary_de": tr["tools"][t["name"]][1]}
                      for t in s["tools"]],
        })
    (HERE / "catalog.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    # --- search.json: client-side search index ---
    search = []
    for s in servers:
        meta = SERVER_META[s["name"]]
        tr = TRANSLATIONS[s["name"]]
        hay = " ".join([
            s["name"], s["title"], s.get("title_de", ""), s["description"],
            tr["desc_fa"], tr["desc_de"], meta["cat"],
            " ".join(t["name"] + " " + t["summary"] + " "
                     + tr["tools"][t["name"]][0] + " "
                     + tr["tools"][t["name"]][1] for t in s["tools"]),
        ])
        search.append({"id": s["name"],
                       "url": "%s/#/en/tool/%s" % (site, s["name"]),
                       "name": s["title"].split(" — ")[0],
                       "en": s["name"], "kind": "mcp", "s": hay})
    (HERE / "search.json").write_text(
        json.dumps(search, indent=2, ensure_ascii=False) + "\n")
    # --- sitemap.xml (home + hash routes + per-server pages + data files) ---
    pages = ["", "marketplace", "builder", "demo", "status", "guide",
             "submit", "connect", "ask", "about", "categories", "skills",
             "tutorials", "blog", "favorites", "my", "privacy", "terms"]
    urls = [site + "/"]
    for lang in ("en", "de", "fa"):
        for p in pages[1:]:
            urls.append("%s/#/%s/%s" % (site, lang, p))
        for s in servers:
            urls.append("%s/#/%s/tool/%s" % (site, lang, s["name"]))
    for f in ("llms.txt", "llms-full.txt", "catalog.json", "search.json",
              ".mcp.json", "submission-guide.md"):
        urls.append("%s/%s" % (site, f))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sm.append('  <url><loc>%s</loc><lastmod>%s</lastmod>'
                  '<changefreq>weekly</changefreq></url>' % (u, today))
    sm.append('</urlset>')
    (HERE / "sitemap.xml").write_text("\n".join(sm) + "\n")
    # --- robots.txt (explicit allow for AI crawlers) ---
    robots = ["User-agent: *", "Allow: /", ""]
    for bot in ("GPTBot", "ClaudeBot", "Claude-SearchBot", "OAI-SearchBot",
                "ChatGPT-User", "PerplexityBot", "Google-Extended"):
        robots += ["User-agent: %s" % bot, "Allow: /", ""]
    robots.append("Sitemap: %s/sitemap.xml" % site)
    (HERE / "robots.txt").write_text("\n".join(robots) + "\n")
    print("wrote .mcp.json + llms.txt + llms-full.txt + catalog.json + "
          "search.json + sitemap.xml + robots.txt:",
          len(servers), "servers")

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

    # --- 3b. Build-date token -> today (detail pages show "last checked") ---
    today = datetime.date.today().isoformat()
    assert "__BUILD_DATE__" in html, "missing __BUILD_DATE__ token"
    html = html.replace("__BUILD_DATE__", today)

    # --- Validation ---
    assert "__COUNTS_" not in html, "unfilled count token left"
    assert "__BUILD_DATE__" not in html, "unfilled build-date token left"
    # all-mcp (2026-11-18): the META object legitimately names the Turkey
    # catalog ("Turkey 32" in its pitch) — it is the meta-server over all
    # three catalogs, not a Turkey migration leftover. Strip the marked
    # META block before the leftover scan; the guard still covers
    # everything else.
    check_html = re.sub(
        r"/\* META-EXEMPT-START \*/.*?/\* META-EXEMPT-END \*/",
        "", html, flags=re.S)
    assert check_html != html, "META exempt block missing from base.html"
    bad = [s for s in ("Turkey", "Türkiye", "Türkçe", "Turkish", "tcmb",
                       "Hepsiburada", "obilet", "arabam", "emlakjet", "armut",
                       "n11", "ciceksepeti", "biletall", "secretcv", "biletix",
                       "sozcu", "eleman", "mackolik", "donanimhaber",
                       "yemek.com", "hurriyet", "sok-mcp", "jolly", "migros",
                       "cineverse", "trthaber",
                       '"tr"', "'tr'", "tr:", "title_tr", "desc_tr",
                       "tag_tr", "gap_tr", "ترکیه")
           if s in check_html]
    # NOTE 2026-11-14: "111 tools" was removed from this list — it was a
    # stale-count canary from the Turkey platform, but 111 is now the
    # legitimate tool count (23 servers). Same false-positive as
    # "22 servers" on 2026-11-13.
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
    write_agent_files(order)
    print("wrote", out, len(html), "chars;",
          n_servers, "server(s),", n_tools, "tools; node --check OK")


if __name__ == "__main__":
    main()
