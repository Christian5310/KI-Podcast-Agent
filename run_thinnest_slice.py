"""Phase 1 (Thinnest Slice): die komplette rohe Kette in einem Lauf.

collect -> select (Platzhalter-Regel) -> script (Claude) -> produce (ElevenLabs) -> out/*.mp3

Bewusst ohne Datenbank, Dedupe, Cross-Check, Faktencheck-Gate - die kommen in
Phase 2 dazu (siehe Strategie_Projektuebersicht, Kapitel 5).

Aufruf: python run_thinnest_slice.py
"""

from datetime import date

from src.collect import collect_all
from src.select import select_placeholder
from src.script import generate_script
from src.produce import produce_audio


def main() -> None:
    print("=== Schritt 1: Sammeln ===")
    raw_items = collect_all()

    print("\n=== Schritt 2: Auswahl (Platzhalter-Regel) ===")
    topics = select_placeholder(raw_items)
    for t in topics:
        print(f"- [{t.source}] {t.title}")

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
