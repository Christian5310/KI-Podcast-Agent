"""Takt 2, Schritt 1: Auswahl - was kommt in die heutige Folge.

Reiner Code (kein Agent) - die Bewertung kommt schon vom Aufbereitungs-Agenten
(process.py) als total_score + themenblock aus der Datenbank. Auswahl ist hier
Sortieren + zwei weiche Regeln aus der Entscheidungstabelle (24.08.2026, Punkt 1):
- max. 30% "Neue Modelle & Releases" pro Folge
- "Gesellschaft & Kontroversen" mind. 2-3x/Woche - wird bevorzugt, wenn die Woche
  noch hinterherhinkt (keine harte Quote, siehe Doku)
"""

from src.db import Client, candidate_topics, week_block_counts

MIN_TOPICS = 4
MAX_TOPICS = 6
MAX_PER_SOURCE = 2
MAX_RELEASES_SHARE = 0.3
GESELLSCHAFT_BLOCK = "Gesellschaft & Kontroversen"
RELEASES_BLOCK = "Neue Modelle & Releases"
GESELLSCHAFT_WEEKLY_TARGET = 2


def _source_key(topic: dict) -> str:
    urls = topic.get("source_urls") or []
    return urls[0].split("/")[2] if urls else "?"


def select_topics(client: Client, n: int = 5) -> list[dict]:
    candidates = candidate_topics(client, limit=30)
    block_counts = week_block_counts(client)
    gesellschaft_so_far = block_counts.get(GESELLSCHAFT_BLOCK, 0)

    # Weiche Prioritaet: liegt die Woche beim Gesellschafts-Block zurueck, ein
    # passendes Thema (falls vorhanden) nach vorne ziehen - keine harte Pflicht,
    # nur Sortierreihenfolge beeinflussen.
    if gesellschaft_so_far < GESELLSCHAFT_WEEKLY_TARGET:
        candidates = sorted(
            candidates, key=lambda t: t.get("themenblock") != GESELLSCHAFT_BLOCK
        )

    per_source_count: dict[str, int] = {}
    releases_count = 0
    max_releases = max(1, round(n * MAX_RELEASES_SHARE))
    selected: list[dict] = []

    for topic in candidates:
        if len(selected) >= n:
            break

        source_key = _source_key(topic)
        if per_source_count.get(source_key, 0) >= MAX_PER_SOURCE:
            continue

        if topic.get("themenblock") == RELEASES_BLOCK and releases_count >= max_releases:
            continue  # Entscheidung 24.08.2026: max. 30% reine Modell-Release-News

        selected.append(topic)
        per_source_count[source_key] = per_source_count.get(source_key, 0) + 1
        if topic.get("themenblock") == RELEASES_BLOCK:
            releases_count += 1

    if len(selected) < MIN_TOPICS:
        print(f"[select] WARNUNG: nur {len(selected)} Themen verfuegbar, Minimum ist {MIN_TOPICS}")

    return selected


if __name__ == "__main__":
    from src.db import get_client

    chosen = select_topics(get_client())
    print(f"Ausgewaehlt ({len(chosen)}):")
    for t in chosen:
        print(f"- [{t['total_score']}] ({t.get('themenblock')}) {t['title']}")
