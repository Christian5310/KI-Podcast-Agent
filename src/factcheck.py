"""Takt 2, Qualitaets-Gate (B6/B7): 2. Modell prueft das FERTIGE Manuskript gegen die Quellen.

Bewusst ein eigener Agent, getrennt vom Aufbereitungs-Agent (process.py): der prueft
Rohfakten VOR dem Schreiben, dieser hier prueft, ob Claude beim Formulieren nichts
verfaelscht/erfunden hat - zwei unabhaengige Kontrollen an zwei verschiedenen Stellen
der Kette (siehe Chat-Diskussion 24.08.2026).

Guenstiges Modell (DeepSeek) - laeuft taeglich + moegliche Retries, muss nicht das
teuerste Modell sein, nur ein anderes als das schreibende (Kriterium 6: unabhaengige
zweite Meinung, nicht "sich selbst kontrollieren").
"""

from openai import OpenAI

from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from src.llm_json import call_json

MODEL = "deepseek-v4-flash"  # deepseek-chat ist laut offizieller Doku abgekuendigt, siehe costs.py
MAX_RETRIES = 2

FACTCHECK_PROMPT = """Du prüfst ein Podcast-Manuskript gegen die Quellen. Suche NUR nach \
harten Faktenfehlern: falsche oder erfundene Zahlen, Namen, Daten oder Ereignisse.

NICHT bemängeln (das ist normal und erwünscht):
- Übersetzung/Umformulierung ins Deutsche, auch wenn nicht wortgleich
- Erkennbare Einordnung/Kommentar des Moderators ("was heißt das konkret", eigene Einschätzung)
- Zusammenfassen oder Weglassen von Details aus der Quelle
- Rhetorische Fragen oder Übergangssätze ohne Faktenbehauptung

NUR bemängeln:
- Eine konkrete Zahl im Manuskript weicht von der Quelle ab (z.B. Manuskript sagt 64, Quelle sagt 65)
- Ein Name/Ereignis/Datum im Manuskript kommt in der Quelle so nicht vor
- Eine als Fakt (nicht als Meinung) formulierte Behauptung ist durch keine Quelle gedeckt

Jeder Eintrag in "issues" ist EIN Satz, eindeutig, ohne Selbstgespräch oder Widerspruch \
in sich. Wenn du unsicher bist, ob etwas ein Fehler ist: NICHT aufnehmen (im Zweifel \
fuer das Manuskript, nur eindeutige Fehler zaehlen).

Antworte NUR mit JSON: {{"passed": true/false, "issues": ["<ein Satz je Fehler>", ...]}}

Quellen:
{sources}

Manuskript:
{script}
"""


def _client() -> OpenAI:
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("DEEPSEEK_API_KEY fehlt in .env")
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=30.0, max_retries=1)


def check_script(script_text: str, topics: list[dict], db_client=None, episode_date=None) -> dict:
    sources = "\n\n".join(
        f"- {t['title']}\n  {t['summary']}\n  Quelle(n): {', '.join(t.get('source_urls', []))}"
        for t in topics
    )
    prompt = FACTCHECK_PROMPT.format(sources=sources, script=script_text)
    return call_json(
        _client(), MODEL, prompt, agent="faktencheck", db_client=db_client, episode_date=episode_date
    )


def generate_with_factcheck(topics: list[dict], db_client=None, episode_date=None,
                             format_: str = "daily", week_context: str | None = None) -> tuple[str, dict, dict]:
    """B7: Manuskript erzeugen, gegenpruefen, bei Fehlschlag mit den gefundenen Problemen
    neu schreiben lassen - bis MAX_RETRIES, danach Abbruch statt Senden (Fehler-Matrix).
    db_client (optional): protokolliert Manuskript- UND Faktencheck-Kosten (Kriterium 6).
    format_/week_context: B4/B5 Sonderformate (Montag-Rueckblick/Freitag-Ueberblick)."""
    from src.script import MODEL as SCRIPT_MODEL
    from src.script import generate_script

    last_result = None
    previous_issues: list[str] | None = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            script_text, usage = generate_script(topics, previous_issues, format_, week_context)
            if db_client is not None:
                from src.db import log_usage

                log_usage(db_client, "manuskript", SCRIPT_MODEL, usage["input_tokens"],
                          usage["output_tokens"], episode_date=episode_date)

            result = check_script(script_text, topics, db_client=db_client, episode_date=episode_date)
        except Exception as exc:
            # API-Fehler zaehlen wie ein nicht bestandener Faktencheck - gleicher
            # Retry-Zaehler, gleicher klarer Abbruch statt undurchsichtigem Crash.
            print(f"[factcheck] Versuch {attempt} mit Fehler abgebrochen: {exc}")
            last_result = {"passed": False, "issues": [f"Technischer Fehler: {exc}"]}
            previous_issues = None
            continue

        print(f"[factcheck] Versuch {attempt}: passed={result['passed']}, "
              f"{len(result.get('issues', []))} Probleme")

        if result["passed"]:
            return script_text, usage, result

        last_result = result
        previous_issues = result.get("issues", [])

    raise RuntimeError(
        f"Faktencheck nach {MAX_RETRIES + 1} Versuchen nicht bestanden - kein Versand. "
        f"Letzte Probleme: {last_result.get('issues') if last_result else '?'}"
    )
