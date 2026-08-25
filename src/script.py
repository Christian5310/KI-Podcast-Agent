"""Takt 2, Schritt 2: Manuskript erzeugen (Zwei-Stimmen-Dialog, ~1.400-1.600 Woerter).

Modell: Claude Sonnet ueber die Anthropic-API (Kap. 4: staerkstes Modell nur fuer
die zwei Qualitaets-Schritte Manuskript + Faktencheck, nicht ueberall - Kriterium 6).
"""

import anthropic

from src.config import ANTHROPIC_API_KEY

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Du schreibst das Manuskript fuer einen taeglichen 10-Minuten \
KI-News-Podcast mit zwei Stimmen im Dialog.

Feste Rollen (in jeder Folge gleich, sorgt fuer wiedererkennbare Chemie statt \
zweier austauschbarer Stimmen):
- A: neugierig, schnell begeistert, stellt gern die "was macht das mit mir"-Frage.
- B: skeptisch-pragmatisch, hakt nach, bremst Hype ein, fragt nach dem Haken.

Redaktions-Grundsatz: Hype-Skepsis statt PR-Uebernahme. Jede Ankuendigung wird \
eingeordnet ("was heisst das konkret"), aber NIE mit derselben Formulierung - \
variiere frei: "Fuer euch heisst das", "Der Haken dabei", "Praktisch gesehen", \
"Und was bedeutet das jetzt wirklich", oder ganz anders, je nach Thema. Wiederholte \
Textbausteine sind selbst eine Schablone - das genaue Gegenteil vom Ziel.

Echte Interaktion statt Frage-Antwort-Schema:
- Mind. 1x pro Folge unterbricht eine Person die andere oder widerspricht.
- Natuerliche, ECHT GESPROCHENE Reaktionen einstreuen (keine Regieanweisungen wie \
  "[raeuspert sich]" - die werden von der Stimme als Text vorgelesen, nicht performt): \
  "Wow, echt?", "Moment, das wusste ich nicht", "Ernsthaft?", "Krass", "Ach so, \
  deswegen", "Naja...", kurze Selbstkorrekturen. Sparsam einsetzen, muss natuerlich \
  wirken, nicht aufgesetzt.
- Nicht jedes Thema gleich lang oder gleich aufgebaut behandeln - manche kurz und \
  punchy, manche mit mehr Tiefe.

Regeln:
- Ziel: 1.400-1.600 Woerter gesprochener Text (10 Minuten).
- Format durchgehend: "A: ..." / "B: ..." pro Zeile, kein Regieanweisungstext.
- Jede Zahl und jeder Eigenname muss aus den gegebenen Themen stammen - nichts erfinden.
- Satzrhythmus mischen: kurze, punchige Saetze UND vereinzelt laengere erklaerende - \
  nicht durchgehend gleich getaktet.
- Einstieg: Die Begruessung ("Willkommen zum taeglichen KI Lab...") kommt bereits \
  VOR dem Dialog durch eine separate Anmoderation - NICHT nochmal begruessen. \
  Der Dialog startet mit einer kurzen, knackigen Vorschau, was heute kommt (1-2 Saetze), \
  dann direkt ins erste Thema.
- Ende: kurzer, nicht formelhafter Abschluss.
"""


def build_user_prompt(topics: list[dict], previous_issues: list[str] | None = None) -> str:
    lines = ["Die heutigen Themen (Titel, Kurzfassung, Quellen, ggf. Fortsetzungshinweis):\n"]
    for i, t in enumerate(topics, 1):
        sources = ", ".join(t.get("source_urls", []))
        entry = f"{i}. {t['title']}\n   {t['summary']}\n   Quelle(n): {sources}"
        if t.get("whats_new"):
            entry += f"\n   FORTSETZUNG - knuepfe am letzten Stand an, das ist neu: {t['whats_new']}"
        lines.append(entry)

    if previous_issues:
        lines.append(
            "\nACHTUNG - der letzte Entwurf hatte folgende Faktenfehler, bitte diesmal vermeiden "
            "(nur schreiben, was oben in den Quellen tatsaechlich steht, im Zweifel weglassen):"
        )
        lines.extend(f"- {issue}" for issue in previous_issues[:8])

    return "\n".join(lines)


def generate_script(topics: list[dict], previous_issues: list[str] | None = None) -> tuple[str, dict]:
    """Erzeugt das Manuskript. Gibt (text, usage_info) zurueck - usage_info fuer
    das Kosten-Logging (D1), auch wenn die DB-Anbindung dafuer erst Phase 3 kommt."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY fehlt in .env")

    # Timeout grosszuegig (eine volle 1.500-Woerter-Antwort braucht teils >60s), plus
    # eigene Retries obendrauf - ein einzelner Verbindungsfehler soll nicht den ganzen
    # Morgenlauf abschiessen (Fehler-Matrix).
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=120.0, max_retries=2)

    last_error = None
    for attempt in range(1, 3):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=8192,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": build_user_prompt(topics, previous_issues)}],
            )
            break
        except anthropic.APIConnectionError as exc:
            last_error = exc
            print(f"[script] Verbindungsfehler (Versuch {attempt}/2): {exc}")
    else:
        raise RuntimeError(f"Claude nach 2 Versuchen nicht erreichbar: {last_error}")

    text = "".join(block.text for block in response.content if block.type == "text")
    usage = {
        "model": MODEL,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text, usage


if __name__ == "__main__":
    from src.db import get_client
    from src.select import select_topics

    topics = select_topics(get_client())
    script_text, usage = generate_script(topics)
    print(f"--- Manuskript ({len(script_text.split())} Woerter, {usage}) ---\n")
    print(script_text)
