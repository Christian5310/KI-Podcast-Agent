"""Takt 2, Schritt 2: Manuskript erzeugen (Zwei-Stimmen-Dialog, ~1.400-1.600 Woerter).

Modell: Claude Sonnet ueber die Anthropic-API (Kap. 4: staerkstes Modell nur fuer
die zwei Qualitaets-Schritte Manuskript + Faktencheck, nicht ueberall - Kriterium 6).
"""

import anthropic

from src.config import ANTHROPIC_API_KEY

MODEL = "claude-sonnet-5"

SYSTEM_PROMPT = """Du schreibst das Manuskript fuer einen taeglichen 10-Minuten \
KI-News-Podcast mit zwei Stimmen im Dialog (Moderator A und Moderator B).

Redaktions-Grundsatz: Hype-Skepsis statt PR-Uebernahme. Jede Ankuendigung wird \
um "was heisst das konkret" ergaenzt, statt sie unkommentiert weiterzugeben.

Regeln:
- Ziel: 1.400-1.600 Woerter gesprochener Text (10 Minuten).
- Format durchgehend: "A: ..." / "B: ..." pro Zeile, kein Regieanweisungstext.
- Jede Zahl und jeder Eigenname muss aus den gegebenen Themen stammen - nichts erfinden.
- Angenehm zu hoeren: kurze Saetze, keine Bandwurmsaetze, klingt gesprochen statt gelesen.
- Am Anfang kurze Begruessung + Ueberblick, am Ende kurzer Abschluss.
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

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY, timeout=60.0, max_retries=1)
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(topics, previous_issues)}],
    )
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
