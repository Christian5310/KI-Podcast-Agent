"""Takt 2, Schritt 1: Auswahl - was kommt in die heutige Folge.

Reiner Code (kein Agent) - die Bewertung ist schon vom Aufbereitungs-Agent (process.py)
als total_score in der Datenbank hinterlegt. Auswahl ist hier nur noch Sortieren +
Filtern, keine inhaltliche Entscheidung mehr (Kap. 3, Modul B1 + Auswahl-Rubrik).
"""

from src.db import Client, candidate_topics

MIN_TOPICS = 4
MAX_TOPICS = 6
MAX_PER_SOURCE = 2


def select_topics(client: Client, n: int = 5) -> list[dict]:
    candidates = candidate_topics(client, limit=30)

    per_source_count: dict[str, int] = {}
    selected: list[dict] = []
    for topic in candidates:
        if len(selected) >= n:
            break
        # source_urls[0] als grobe Quellen-Kennung fuer die Streuungsregel
        source_key = topic["source_urls"][0].split("/")[2] if topic.get("source_urls") else "?"
        if per_source_count.get(source_key, 0) >= MAX_PER_SOURCE:
            continue
        selected.append(topic)
        per_source_count[source_key] = per_source_count.get(source_key, 0) + 1

    if len(selected) < MIN_TOPICS:
        print(f"[select] WARNUNG: nur {len(selected)} Themen verfuegbar, Minimum ist {MIN_TOPICS}")

    return selected


if __name__ == "__main__":
    from src.db import get_client

    chosen = select_topics(get_client())
    print(f"Ausgewaehlt ({len(chosen)}):")
    for t in chosen:
        print(f"- [{t['total_score']}] {t['title']}")
