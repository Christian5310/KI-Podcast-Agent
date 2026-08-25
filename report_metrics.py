"""D7 + Kriterium 6: schneller Bericht fuer die Mittwoch-Vorstellung.

Aufruf: python report_metrics.py
"""

from src.db import cost_summary, get_client, repetition_metric


def main() -> None:
    client = get_client()

    print("=== Wiederholungs-Metrik (D7, Kriterium 2/3) ===")
    rep = repetition_metric(client)
    print(f"{rep['episodes_compared']} Folgen verglichen, "
          f"durchschnittliche Themen-Ueberlappung: {rep['avg_overlap'] * 100:.1f}%")
    for p in rep["pairs"]:
        print(f"  {p['from']} -> {p['to']}: {p['overlap'] * 100:.1f}% Ueberlappung")

    print("\n=== Kosten (Kriterium 6) ===")
    rows = cost_summary(client)
    total = sum(r["cost_eur"] for r in rows)
    for r in rows:
        print(f"  {r['agent']:14s} {r['model']:20s} {r['calls']:4d}x  {r['cost_eur']:.4f} EUR")
    print(f"\nGESAMT bisher: {total:.4f} EUR")


if __name__ == "__main__":
    main()
