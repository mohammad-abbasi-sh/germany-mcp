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
