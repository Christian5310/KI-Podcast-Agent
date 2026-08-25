"""Takt 1, Schritt 2: Aufbereitung - der Aufbereitungs-Agent (1 Agent, guenstiges Modell).

Pro Rohartikel EIN DeepSeek-Aufruf, der beantwortet:
- Haben wir das schon? (Dedupe gegen die letzten 14 Tage, A2)
- Ist es eine Fortsetzung, und was genau ist neu? (A4)
- Bewertung nach der Auswahl-Rubrik (Kap. 3) -> macht select.py zu reinem Code (kein Agent dort)

Cross-Check ("stimmt das ueberhaupt", Kriterium 5, A3) ist ein zweiter, separater Schritt
mit Exa-Suche - laeuft nur fuer Themen, die es potenziell in die Folge schaffen koennten
(nicht schon_bekannt), nicht fuer jeden Rohartikel. Ohne EXA_API_KEY: verified=None
(ungeprueft markiert, nicht geraten - besser ehrlich unsicher als falsch behauptet).

Gewichtung der Rubrik (Kap. 3, angepasst auf Zielgruppe KI-Alltagsuser 24.08.2026):
Neuheit x3, Handlungsbezug x3 (Alltagsuser-Aequivalent zu "Mittelstandsrelevanz"),
Quellenbreite x2, Aktualitaet x2. Max. 100 Punkte.
"""

import threading
from datetime import datetime, timezone

from exa_py import Exa
from openai import OpenAI

from src.collect import RawItem
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, EXA_API_KEY
from src.llm_json import call_json

MODEL = "deepseek-v4-flash"  # deepseek-chat ist laut offizieller Doku abgekuendigt, siehe costs.py

WEIGHTS = {"neuheit": 3, "handlungsbezug": 3, "quellenbreite": 2, "aktualitaet": 2}

# Entscheidung 24.08.2026 (Entscheidungstabelle Quellenbewertung, Punkt 3): max. 72h.
MAX_AGE_HOURS = 72

TRIAGE_PROMPT = """Du bewertest eine KI-News-Rohmeldung fuer einen taeglichen KI-Podcast \
fuer KI-Alltagsuser (nicht zu technisch, nicht zu einschlaegig, nutzerorientiert - \
"was heisst das fuer mich").

Vergleiche sie mit den zuletzt bekannten Themen unten (nummeriert). Antworte NUR mit JSON, \
kein Fliesstext davor/danach:

{{
  "schon_bekannt": true/false,
  "ist_fortsetzung": true/false,
  "passendes_thema_index": <int oder null>,
  "was_ist_neu": "<string oder null>",
  "kernbehauptung": "<die zentrale pruefbare Tatsache: Zahl, Name oder Fakt>",
  "themenblock": "<einer von: Neue Modelle & Releases | Tools & Alltag | Kosten & Zugang | Gesellschaft & Kontroversen | Forschung & Ausblick | Unternehmen & Markt>",
  "scores": {{"neuheit": <0-10>, "quellenbreite": <0-10>, "aktualitaet": <0-10>, "handlungsbezug": <0-10>}}
}}

schon_bekannt=true UND ist_fortsetzung=false bedeutet: reine Wiederholung, nichts Neues -> neuheit=0.
Fuer "aktualitaet": nutze das Alter unten direkt (0-6h -> 9-10, 6-24h -> 6-8, 24-48h -> 3-5,
48-72h -> 0-2), nicht die reine Textwirkung schaetzen.

Bekannte Themen der letzten 14 Tage:
{known_topics}

Neue Rohmeldung:
Titel: {title}
Quelle: {source}
Alter: {age}
Zusammenfassung: {summary}
"""

VERIFY_PROMPT = """Pruefe anhand der Suchergebnisse, ob diese Behauptung durch unabhaengige \
Quellen gedeckt ist. Antworte NUR mit JSON: {{"verified": true/false, "note": "<1 Satz Begruendung"}}

Behauptung: {claim}

Suchergebnisse:
{search_results}
"""


def _client() -> OpenAI:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY fehlt in .env")
    # Timeout gesetzt, damit ein einzelner haengender Call nicht den ganzen Lauf blockiert -
    # call_json() versucht es danach automatisch erneut (Fehler-Matrix).
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=30.0, max_retries=1)


def _age_str(item: RawItem) -> str:
    if not item.published:
        return "unbekannt (vorsichtig/niedrig bewerten)"
    hours = (datetime.now(timezone.utc) - item.published).total_seconds() / 3600
    return f"{hours:.0f} Stunden alt"


def triage_item(client: OpenAI, item: RawItem, known_topics: list[dict], db_client=None) -> dict:
    known_str = "\n".join(f"{i}. {t['title']}" for i, t in enumerate(known_topics)) or "(keine)"
    prompt = TRIAGE_PROMPT.format(
        known_topics=known_str, title=item.title, source=item.source,
        age=_age_str(item), summary=item.summary,
    )
    return call_json(client, MODEL, prompt, agent="aufbereitung", db_client=db_client)


def cross_check(client: OpenAI, claim: str, db_client=None) -> dict:
    """Sucht mit Exa nach der Kernbehauptung und laesst DeepSeek beurteilen, ob sie gedeckt ist."""
    if not EXA_API_KEY:
        return {"verified": None, "note": "Kein EXA_API_KEY - ungeprueft, nicht geraten"}

    exa = Exa(api_key=EXA_API_KEY)
    results = exa.search(claim, num_results=3)
    snippets = "\n\n".join(f"- {r.title} ({r.url})\n  {(r.text or '')[:400]}" for r in results.results)
    if not snippets:
        return {"verified": None, "note": "Keine Suchergebnisse gefunden"}

    return call_json(
        client, MODEL, VERIFY_PROMPT.format(claim=claim, search_results=snippets),
        agent="aufbereitung", db_client=db_client,
    )


def score_total(scores: dict) -> float:
    return sum(scores.get(k, 0) * w for k, w in WEIGHTS.items())


ITEM_TIMEOUT_SECONDS = 45


def _process_one(client: OpenAI, item: RawItem, known_topics: list[dict], db_client) -> dict | None:
    """Ein Rohartikel: Triage + ggf. Cross-Check. None = reine Wiederholung, raus."""
    triage = triage_item(client, item, known_topics, db_client=db_client)
    if triage.get("schon_bekannt") and not triage.get("ist_fortsetzung"):
        return None

    claim = triage.get("kernbehauptung")
    if claim:
        verification = cross_check(client, claim, db_client=db_client)
    else:
        verification = {"verified": None, "note": "Keine pruefbare Kernbehauptung vom Agenten geliefert"}

    idx = triage.get("passendes_thema_index")
    parent_id = known_topics[idx]["id"] if isinstance(idx, int) and 0 <= idx < len(known_topics) else None
    scores = triage.get("scores") or {}

    return {
        "title": item.title,
        "summary": item.summary,
        "source_urls": [item.url],
        "parent_topic_id": parent_id,
        "whats_new": triage.get("was_ist_neu"),
        "themenblock": triage.get("themenblock"),
        "scores": scores,
        "total_score": score_total(scores),
        "verified": verification["verified"],
        "verification_note": verification["note"],
    }


def _process_one_with_timeout(client: OpenAI, item: RawItem, known_topics: list[dict], db_client) -> dict | None:
    """Haertester Schutz: weder die DeepSeek- noch die Exa-Bibliothek erlauben ein
    zuverlaessiges Timeout (Exa hat gar keinen Parameter dafuer). Deshalb laeuft die
    Verarbeitung in einem Daemon-Thread - haengt ein Call, geben wir nach
    ITEM_TIMEOUT_SECONDS auf und machen mit dem naechsten Artikel weiter, statt den
    ganzen Lauf zu blockieren. Der haengende Thread stirbt spaetestens mit dem Prozess."""
    box: dict = {}

    def target():
        try:
            box["result"] = _process_one(client, item, known_topics, db_client)
        except Exception as exc:
            box["error"] = exc

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(ITEM_TIMEOUT_SECONDS)

    if thread.is_alive():
        print(f"[process] TIMEOUT nach {ITEM_TIMEOUT_SECONDS}s bei {item.title[:60]!r} - uebersprungen")
        return None
    if "error" in box:
        print(f"[process] FEHLER bei {item.title[:60]!r}: {box['error']} - uebersprungen")
        return None
    return box.get("result")


MAX_WORKERS = 8  # parallele Artikel gleichzeitig - sequentiell haette ~180 Artikel weit
                 # ueber eine Stunde gebraucht (in der CI beobachtet, 24.08.2026)


def process_items(raw_items: list[RawItem], known_topics: list[dict], on_result=None,
                   db_client=None) -> list[dict]:
    """Verarbeitet alle Rohartikel PARALLEL (Thread-Pool, siehe MAX_WORKERS), gibt Liste
    fertiger Themen-Datensaetze zurueck. Reine Wiederholungen werden herausgefiltert.
    on_result(dict) wird nach JEDEM fertigen Artikel aufgerufen (z.B. sofort in die DB
    schreiben) - damit bei einem Fehler mittendrin nicht die bereits erledigte Arbeit
    verloren geht (Fehler-Matrix). db_client (optional): wenn gesetzt, wird jeder
    Modellaufruf sofort mit Kosten protokolliert (Kriterium 6, usage_log)."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    client = _client()
    results = []
    skipped_old = 0
    to_process = []

    for item in raw_items:
        if item.published:
            age_hours = (datetime.now(timezone.utc) - item.published).total_seconds() / 3600
            if age_hours > MAX_AGE_HOURS:
                skipped_old += 1
                continue  # Entscheidung 24.08.2026: aelter als 72h kommt gar nicht erst rein
        to_process.append(item)

    print(f"[process] {len(to_process)} Artikel werden mit {MAX_WORKERS} parallelen "
          f"Workern verarbeitet...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_to_item = {
            pool.submit(_process_one_with_timeout, client, item, known_topics, db_client): item
            for item in to_process
        }
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            record = future.result()  # _process_one_with_timeout faengt selbst alle Fehler ab
            if record is None:
                continue

            results.append(record)
            print(f"[process] {item.title[:60]!r} -> score={record['total_score']:.0f}, "
                  f"verified={record['verified']}")

            if on_result:
                on_result(record)

    if skipped_old:
        print(f"[process] {skipped_old} Rohartikel wegen Alter (>{MAX_AGE_HOURS}h) uebersprungen, "
              f"kein Agent-Aufruf noetig")

    return results


if __name__ == "__main__":
    from src.collect import collect_all

    items = collect_all()[:5]  # kleiner Testlauf, nicht alle 155 auf einmal (Kosten!)
    processed = process_items(items, known_topics=[])
    print(f"\n{len(processed)}/{len(items)} Themen mit Neuigkeitswert:")
    for p in processed:
        print(f"- [{p['total_score']:.0f}] {p['title']}")
