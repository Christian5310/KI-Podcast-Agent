"""Takt 2, Schritt 3: Produktion - Manuskript zu Audio (Zwei-Stimmen-TTS).

TODO: an TTS-Anbieter anbinden, sobald geklaert (ElevenLabs vermutlich,
siehe Chat). parse_dialogue() ist schon einsatzbereit.
"""

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "out"


def parse_dialogue(script_text: str) -> list[tuple[str, str]]:
    """Zerlegt 'A: ...' / 'B: ...' Zeilen in (Sprecher, Text)-Paare."""
    lines = []
    for raw_line in script_text.strip().splitlines():
        raw_line = raw_line.strip()
        if not raw_line or ":" not in raw_line:
            continue
        speaker, text = raw_line.split(":", 1)
        speaker = speaker.strip()
        if speaker in ("A", "B"):
            lines.append((speaker, text.strip()))
    return lines


def produce_audio(script_text: str, episode_date: str) -> Path:
    """TODO: pro Dialogzeile TTS-Call (Stimme A/B), Segmente zusammensetzen, als mp3 ablegen."""
    raise NotImplementedError(
        "TTS-Anbieter noch offen (siehe Chat) - parse_dialogue() ist bereits einsatzbereit."
    )
