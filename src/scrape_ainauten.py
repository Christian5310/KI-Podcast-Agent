"""Nicht-RSS-Quelle: AInauten Newsletter (beehiiv, kein oeffentlicher RSS-Feed
gefunden - mehrere ueblichen Muster geprueft, alle 404). Das Archiv unter
/t/newsletter ist aber serverseitig gerendertes HTML (kein Headless-Browser
noetig), nur mit einer no-code Page-Builder-Struktur ohne stabile data-Attribute.

Bruechiger als ein echter RSS-Feed: Titel und Datum werden ueber Reihenfolge im
HTML gepaart (funktioniert, weil beehiiv beides in derselben Kartenreihenfolge
rendert - getestet 24.08.2026, 25 Titel / 25 Daten, exakt passend). Bricht,
wenn AInauten ihr Seiten-Template aendert.
"""

import re
from datetime import datetime, timezone

import requests

from src.collect import MAX_SUMMARY_CHARS, RawItem, _strip_html

ARCHIVE_URL = "https://www.ainauten.com/t/newsletter"
BASE_URL = "https://www.ainauten.com"
MAX_AGE_DAYS = 4  # großzuegiger Vorfilter - der echte 72h-Cutoff kommt in process.py

_MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def _parse_date(text: str) -> datetime | None:
    m = re.match(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})", text)
    if not m or m.group(1) not in _MONTHS:
        return None
    mon, day, year = m.groups()
    return datetime(int(year), _MONTHS[mon], int(day), tzinfo=timezone.utc)


def _fetch_article_body(url: str) -> str:
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        return _strip_html(resp.text)[:MAX_SUMMARY_CHARS]
    except Exception as exc:
        print(f"[ainauten] WARNUNG Artikeltext nicht ladbar ({url}): {exc}")
        return ""


def fetch_ainauten() -> list[RawItem]:
    resp = requests.get(ARCHIVE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    resp.raise_for_status()
    html = resp.text

    titles = re.findall(r'<a href="(/p/[^"]+)"[^>]*aria-label="([^"]+)"', html)
    dates = re.findall(r'>([A-Z][a-z]{2} \d{1,2}, \d{4})<', html)

    if len(titles) != len(dates):
        print(f"[ainauten] WARNUNG: {len(titles)} Titel vs. {len(dates)} Daten - "
              f"Seiten-Template hat sich vermutlich geaendert, ueberspringe")
        return []

    now = datetime.now(timezone.utc)
    items: list[RawItem] = []
    seen: set[str] = set()

    for (href, title), date_str in zip(titles, dates):
        if href in seen:
            continue
        seen.add(href)

        published = _parse_date(date_str)
        if published and (now - published).days > MAX_AGE_DAYS:
            continue  # Archiv ist chronologisch, aeltere Eintraege danach ignorieren wir

        url = BASE_URL + href
        items.append(RawItem(source="AInauten", title=title, url=url,
                              summary=_fetch_article_body(url), published=published))

    return items


if __name__ == "__main__":
    for item in fetch_ainauten():
        print(f"- [{item.published}] {item.title}\n  {item.url}\n  {len(item.summary)} Zeichen Text")
