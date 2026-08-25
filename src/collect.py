"""Takt 1, Schritt 1: Quellen abrufen (Sammeln).

Holt Rohnachrichten aus den in config.FEEDS definierten RSS-Feeds.
Bewusst dumm: keine Bewertung, keine Deduplizierung, keine KI - das ist
gewoehnlicher Python-Code (siehe Ausschreibung: "Wo ihr Agenten braucht und
wo nicht"). Dedupe/Cross-Check/Fortsetzungserkennung kommen in process.py
(Phase 2).

Test direkt ausfuehrbar: python -m src.collect
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser

from src.config import FEEDS, Feed

_TAG_RE = re.compile(r"<[^>]+>")
MAX_SUMMARY_CHARS = 3000  # genug fuer Faktencheck, ohne Prompts unnoetig aufzublaehen


@dataclass
class RawItem:
    source: str
    title: str
    url: str
    summary: str
    published: datetime | None


def _strip_html(raw: str) -> str:
    return _TAG_RE.sub(" ", raw).replace("&nbsp;", " ").replace("&amp;", "&").strip()


def _best_text(entry) -> str:
    """Nimmt den vollstaendigsten verfuegbaren Text (RSS 'summary' ist oft nur ein
    Teaser-Satz, viele Feeds liefern in 'content' den vollen/laengeren Artikeltext -
    wichtig, damit Manuskript- und Faktencheck-Agent genug Substanz zum Pruefen haben)."""
    candidates = []
    if entry.get("content"):
        candidates.append(entry["content"][0].get("value", ""))
    if entry.get("summary"):
        candidates.append(entry["summary"])
    best = max(candidates, key=len, default="")
    return _strip_html(best)[:MAX_SUMMARY_CHARS]


def _parse_published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(mktime(value), tz=timezone.utc)
    return None


_USER_AGENT = "ki-lab-podcast-agent/1.0 (taeglicher KI-News-Podcast; +https://github.com/Christian5310/KI-Podcast-Agent)"


def fetch_feed(feed: Feed) -> list[RawItem]:
    # Eigener User-Agent statt feedparser-Default - manche Quellen (v.a. Reddit)
    # blocken/rate-limiten generische Bot-User-Agents haerter.
    parsed = feedparser.parse(feed.url, agent=_USER_AGENT)
    items = []
    for entry in parsed.entries:
        items.append(
            RawItem(
                source=feed.name,
                title=entry.get("title", "").strip(),
                url=entry.get("link", "").strip(),
                summary=_best_text(entry),
                published=_parse_published(entry),
            )
        )
    return items


def collect_all(feeds: list[Feed] = FEEDS) -> list[RawItem]:
    all_items: list[RawItem] = []
    for feed in feeds:
        try:
            items = fetch_feed(feed)
            print(f"[collect] {feed.name}: {len(items)} Eintraege")
            all_items.extend(items)
        except Exception as exc:  # Fehler-Matrix: einzelne Quelle darf ausfallen
            print(f"[collect] WARNUNG {feed.name} nicht erreichbar: {exc}")

    # Nicht-RSS-Quellen (lokaler Import gegen Zirkelimport, siehe scrape_ainauten.py)
    from src.scrape_ainauten import fetch_ainauten

    try:
        items = fetch_ainauten()
        print(f"[collect] AInauten: {len(items)} Eintraege")
        all_items.extend(items)
    except Exception as exc:
        print(f"[collect] WARNUNG AInauten nicht erreichbar: {exc}")

    return all_items


if __name__ == "__main__":
    results = collect_all()
    print(f"\nGesamt: {len(results)} Rohnachrichten aus {len(FEEDS)} RSS-Feeds + AInauten\n")
    for item in results[:5]:
        print(f"- [{item.source}] {item.title}\n  {item.url}")
