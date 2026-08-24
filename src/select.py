"""Takt 2, Schritt 1: Auswahl - was kommt in die heutige Folge.

Phase 1 (Thinnest Slice): regelbasierter Platzhalter ohne DB-Anbindung -
nimmt einfach die juengsten N Eintraege aus den frisch gesammelten Rohdaten.
KEIN Scoring, KEIN Dedupe, KEINE Quellen-Datenbank. Bewusst grob, siehe
Leitprinzip in Kap. 5.

Phase 2 ersetzt select_placeholder() durch die richtige Auswahl-Rubrik
(Kap. 3, Modul B) gegen die Supabase-Datenbank statt gegen Rohdaten.
"""

from src.collect import RawItem

MIN_TOPICS = 4
MAX_TOPICS = 6


def select_placeholder(items: list[RawItem], n: int = 5) -> list[RawItem]:
    """Platzhalter-Regel: neueste zuerst, je Quelle max. 2, insgesamt n."""
    per_source_count: dict[str, int] = {}
    sorted_items = sorted(items, key=lambda i: i.published or 0, reverse=True)

    selected: list[RawItem] = []
    for item in sorted_items:
        if len(selected) >= n:
            break
        if not item.title or not item.url:
            continue
        count = per_source_count.get(item.source, 0)
        if count >= 2:
            continue
        selected.append(item)
        per_source_count[item.source] = count + 1

    return selected


if __name__ == "__main__":
    from src.collect import collect_all

    raw = collect_all()
    chosen = select_placeholder(raw)
    print(f"\nAusgewaehlt ({len(chosen)}):")
    for item in chosen:
        print(f"- [{item.source}] {item.title}")
