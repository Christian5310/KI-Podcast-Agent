"""Phase 1 (Thinnest Slice): die komplette rohe Kette in einem Lauf.

collect -> select (Platzhalter-Regel) -> script (Claude) -> produce (ElevenLabs) -> out/*.mp3

Bewusst ohne Datenbank, Dedupe, Cross-Check, Faktencheck-Gate - die kommen in
Phase 2 dazu (siehe Strategie_Projektuebersicht, Kapitel 5).

Aufruf: python run_thinnest_slice.py
"""

from datetime import date

from src.collect import RawItem, collect_all
from src.script import generate_script
from src.produce import produce_audio

# Phase 2 hat select_placeholder() aus src/select.py entfernt - dort steht jetzt
# select_topics(), das gegen die Supabase-Datenbank arbeitet. Dieses Skript soll
# aber bewusst OHNE Datenbank laufen, deshalb steht die Platzhalter-Regel hier
# lokal. Unveraendert die Fassung aus Commit 75c8dee^.
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


def as_topic_dicts(items: list[RawItem]) -> list[dict]:
    """RawItem -> das dict-Format, das generate_script() seit Phase 2 erwartet.

    In Phase 2 kommen die Themen aufbereitet aus der Datenbank (title, summary,
    source_urls). Hier gibt es nur Rohdaten, also wird die Rohzusammenfassung
    durchgereicht und die eine Quell-URL in eine Liste gepackt.
    """
    return [
        {"title": i.title, "summary": i.summary, "source_urls": [i.url]}
        for i in items
    ]


def main() -> None:
    print("=== Schritt 1: Sammeln ===")
    raw_items = collect_all()

    print("\n=== Schritt 2: Auswahl (Platzhalter-Regel) ===")
    selected = select_placeholder(raw_items)
    for t in selected:
        print(f"- [{t.source}] {t.title}")
    topics = as_topic_dicts(selected)

    print("\n=== Schritt 3: Manuskript (Claude) ===")
    script_text, usage = generate_script(topics)
    print(f"{len(script_text.split())} Woerter | Token-Nutzung: {usage}")

    episode_date = date.today().isoformat()
    script_path = f"out/{episode_date}.md"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"Manuskript geschrieben: {script_path}")

    print("\n=== Schritt 4: Produktion (ElevenLabs) ===")
    audio_path = produce_audio(script_text, episode_date)
    print(f"Audio geschrieben: {audio_path}")

    print("\n=== Fertig: Thinnest Slice einmal komplett durchgelaufen ===")


if __name__ == "__main__":
    main()
