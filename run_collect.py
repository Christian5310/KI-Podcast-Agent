"""Takt 1 (Sammeln & Aufbereiten): laeuft unabhaengig vom Morgenlauf, beliebig oft.

collect (Code) -> process (Aufbereitungs-Agent) -> Supabase (Themen-Gedaechtnis)

Aufruf: python run_collect.py
"""

from src.collect import collect_all
from src.db import get_client, insert_topic, recent_topics
from src.process import process_items


def main() -> None:
    client = get_client()

    print("=== Sammeln ===")
    raw_items = collect_all()

    print("\n=== Bekannte Themen laden (letzte 14 Tage) ===")
    known = recent_topics(client, days=14)
    print(f"{len(known)} bekannte Themen")

    print("\n=== Aufbereitung (Agent) + laufendes Speichern ===")
    processed = process_items(
        raw_items, known, on_result=lambda t: insert_topic(client, t), db_client=client
    )

    print(f"\nFertig: {len(processed)} Themen gespeichert.")


if __name__ == "__main__":
    main()
