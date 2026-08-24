"""Takt 1, Schritt 1: Quellen abrufen (Sammeln).

Holt Rohnachrichten aus den in config.FEEDS definierten RSS-Feeds.
Bewusst dumm: keine Bewertung, keine Deduplizierung, keine KI - das ist
gewoehnlicher Python-Code (siehe Ausschreibung: "Wo ihr Agenten braucht und
wo nicht"). Dedupe/Cross-Check/Fortsetzungserkennung kommen in process.py
(Phase 2).

Test direkt ausfuehrbar: python -m src.collect
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from time import mktime

import feedparser

from src.config import FEEDS, Feed


@dataclass
class RawItem:
    source: str
    title: str
    url: str
    summary: str
    published: datetime | None


def _parse_published(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            return datetime.fromtimestamp(mktime(value), tz=timezone.utc)
    return None


def fetch_feed(feed: Feed) -> list[RawItem]:
    parsed = feedparser.parse(feed.url)
    items = []
    for entry in parsed.entries:
        items.append(
            RawItem(
                source=feed.name,
                title=entry.get("title", "").strip(),
                url=entry.get("link", "").strip(),
                summary=entry.get("summary", "").strip(),
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
    return all_items


if __name__ == "__main__":
    results = collect_all()
    print(f"\nGesamt: {len(results)} Rohnachrichten aus {len(FEEDS)} Quellen\n")
    for item in results[:5]:
        print(f"- [{item.source}] {item.title}\n  {item.url}")
