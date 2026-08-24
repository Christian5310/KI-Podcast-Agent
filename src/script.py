"""Takt 2, Schritt 2: Manuskript erzeugen (Zwei-Stimmen-Dialog, ~1.400-1.600 Woerter).

Der Prompt-Aufbau ist fertig, der eigentliche LLM-Call ist ein TODO -
haengt von der Modell-Entscheidung (Claude/DeepSeek/Gemini) ab, siehe Chat.
Sobald geklaert: generate_script() unten fertigstellen.
"""

from src.collect import RawItem

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


def build_user_prompt(topics: list[RawItem]) -> str:
    lines = ["Die heutigen Themen (Titel, Quelle, Kurzfassung, URL):\n"]
    for i, t in enumerate(topics, 1):
        lines.append(f"{i}. {t.title} [{t.source}]\n   {t.summary}\n   Quelle: {t.url}\n")
    return "\n".join(lines)


def generate_script(topics: list[RawItem]) -> str:
    """TODO: an gewaehltes Modell anbinden, sobald API-Zugang geklaert ist."""
    raise NotImplementedError(
        "Modellwahl fuer Manuskript noch offen (Claude/DeepSeek/Gemini) - "
        "siehe Chat. build_user_prompt() ist bereits einsatzbereit."
    )
