"""Takt 2 (Morgenlauf): Auswahl -> Manuskript+Faktencheck -> Produktion -> Ablage.

Nimmt NUR, was Takt 1 (run_collect.py) schon in die Datenbank geschrieben hat -
keine Live-Recherche hier (Zeitkritisch, muss vor 8:00 Uhr fertig sein).

Aufruf: python run_morning.py
"""

from datetime import date

from src.db import get_client, insert_episode, mark_topics_used
from src.factcheck import generate_with_factcheck
from src.produce import produce_audio
from src.select import select_topics


def main() -> None:
    client = get_client()
    episode_date = date.today()

    print("=== Auswahl (Code, Scores aus der DB) ===")
    topics = select_topics(client)
    for t in topics:
        print(f"- [{t['total_score']}] {t['title']}")

    print("\n=== Manuskript + Faktencheck-Gate ===")
    script_text, usage, factcheck_result = generate_with_factcheck(topics)
    print(f"{len(script_text.split())} Woerter, Faktencheck bestanden: {factcheck_result['passed']}")

    script_path = f"out/{episode_date.isoformat()}.md"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)

    print("\n=== Produktion ===")
    audio_path = produce_audio(script_text, episode_date.isoformat())
    print(f"Audio: {audio_path}")

    print("\n=== Ablegen & Themen als 'verwendet' markieren ===")
    insert_episode(client, episode_date, script_text)
    mark_topics_used(client, [t["id"] for t in topics], episode_date)

    print(f"\n=== Fertig: Folge vom {episode_date.isoformat()} ===")


if __name__ == "__main__":
    main()
