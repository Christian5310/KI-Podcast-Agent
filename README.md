# AGENTTEST
WAS DIESES PROJEKT TUT: NOCH NICHT GESCHRIEBEN.
## Das braucht ihr, bevor ihr anfangt
## So startet ihr es
## Das gehört in die .env
## Das haben wir bewusst so gebaut
# Der Podcast — KI-News, automatisiert

Antwort auf die FBS-Ausschreibung "Der Podcast" (Kurs KI-Manager). Vollstaendige
Architektur, Anforderungen und Entscheidungslog: siehe
[`Strategie_Projektuebersicht_KI-Podcast_24.08.2026.md`](Strategie_Projektuebersicht_KI-Podcast_24.08.2026.md).

## Zwei Takte

- **Takt 1** (`collect.py` → `process.py` → Supabase): sammelt & bereitet auf, nicht zeitkritisch.
- **Takt 2** (`select.py` → `script.py` → `produce.py`): der Morgenlauf, fertig vor 8:00 Uhr.

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env   # ausfuellen
```

## Aktueller Stand

Thinnest-Slice-Aufbau (Phase 1, Kap. 5): `collect.py` und `select.py` laufen bereits
(`python -m src.collect`, `python -m src.select`). `script.py`/`produce.py` warten auf
die Modell-/TTS-Entscheidung. `db.py` + `supabase/schema.sql` sind vorbereitet fuer
Phase 2, sobald das Supabase-Projekt feststeht.
