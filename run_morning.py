"""Takt 2 (Morgenlauf): Auswahl -> Manuskript+Faktencheck -> Produktion -> Zustellung.

Nimmt NUR, was Takt 1 (run_collect.py) schon in die Datenbank geschrieben hat -
keine Live-Recherche hier (Zeitkritisch, muss vor 8:00 Uhr fertig sein).

Die Zustellung (Website/RSS aktualisieren) ist bewusst der LETZTE Schritt, erst
nachdem Manuskript, Faktencheck und Produktion erfolgreich durchgelaufen sind -
das ist der Fehler-Matrix-Fallback (C4): schlaegt irgendwas vorher fehl, wird
site/ nicht angefasst, die Vortagesfolge bleibt online.

Aufruf: python run_morning.py [--date 2026-08-22]   (--date fuer Backfill, D4)
"""

import argparse
from datetime import date

from src.db import get_client, insert_episode, mark_topics_used, upload_audio
from src.deliver import build_site
from src.factcheck import generate_with_factcheck
from src.produce import produce_audio
from src.select import select_topics


def main(episode_date: date) -> None:
    client = get_client()

    print("=== Auswahl (Code, Scores aus der DB) ===")
    topics = select_topics(client)
    for t in topics:
        print(f"- [{t['total_score']}] {t['title']}")

    print("\n=== Manuskript + Faktencheck-Gate ===")
    script_text, usage, factcheck_result = generate_with_factcheck(
        topics, db_client=client, episode_date=episode_date
    )
    print(f"{len(script_text.split())} Woerter, Faktencheck bestanden: {factcheck_result['passed']}")

    script_path = f"out/{episode_date.isoformat()}.md"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)

    print("\n=== Produktion ===")
    audio_path = produce_audio(script_text, episode_date.isoformat())
    print(f"Audio lokal: {audio_path}")

    print("\n=== Hochladen (oeffentlich erreichbar, C2) ===")
    audio_url = upload_audio(client, audio_path, episode_date)
    print(f"Audio oeffentlich: {audio_url}")

    print("\n=== Ablegen & Themen als 'verwendet' markieren ===")
    topic_ids = [t["id"] for t in topics]
    episode = insert_episode(client, episode_date, script_text, audio_url=audio_url, topic_ids=topic_ids)
    mark_topics_used(client, topic_ids, episode_date)

    print("\n=== Zustellung aktualisieren (C3, letzter Schritt) ===")
    build_site()

    print(f"\n=== Fertig: Folge vom {episode_date.isoformat()} ===")
    print(f"Kosten Manuskript+Faktencheck: {episode['cost_eur']:.4f} EUR "
          f"({episode['model_usage']}) - TTS-Kosten separat, noch nicht mitgezaehlt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=date.fromisoformat, default=date.today(),
                         help="Fuer Backfill (D4): Folge nachtraeglich fuer einen vergangenen Tag erzeugen")
    args = parser.parse_args()
    main(args.date)
