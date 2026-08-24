"""Takt 2, Schritt 3: Produktion - Manuskript zu Audio (Zwei-Stimmen-TTS via ElevenLabs).

Je Dialogzeile ein TTS-Call (Stimme A oder B), Segmente werden aneinandergehaengt.
Voice-IDs sind Platzhalter aus der ElevenLabs-Standardbibliothek - im ElevenLabs-
Dashboard (Voice Library) pruefen/durch eigene Wahl ersetzen (siehe .env).
"""

import os
from pathlib import Path

import requests

from src.config import ELEVENLABS_API_KEY

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

VOICE_A = os.environ.get("ELEVENLABS_VOICE_A", "21m00Tcm4TlvDq8ikWAM")  # Platzhalter, in ElevenLabs pruefen
VOICE_B = os.environ.get("ELEVENLABS_VOICE_B", "pNInz6obpgDQGcFmaJgB")  # Platzhalter, in ElevenLabs pruefen


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


def _tts_segment(text: str, voice_id: str) -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY fehlt in .env")
    resp = requests.post(
        TTS_URL.format(voice_id=voice_id),
        headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": "eleven_multilingual_v2"},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.content


def produce_audio(script_text: str, episode_date: str) -> Path:
    """Fuegt pro Dialogzeile ein TTS-Segment an, schreibt eine mp3 nach out/."""
    lines = parse_dialogue(script_text)
    if not lines:
        raise ValueError("Kein verwertbarer Dialog im Manuskript gefunden (Format 'A: ...' / 'B: ...' erwartet)")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{episode_date}.mp3"

    with open(out_path, "wb") as f:
        for i, (speaker, text) in enumerate(lines, 1):
            voice_id = VOICE_A if speaker == "A" else VOICE_B
            audio = _tts_segment(text, voice_id)
            f.write(audio)
            print(f"[produce] Segment {i}/{len(lines)} ({speaker}) geschrieben")

    return out_path


if __name__ == "__main__":
    from datetime import date

    sample = "A: Willkommen zur Testfolge.\nB: Schoen, dass du dabei bist."
    path = produce_audio(sample, date.today().isoformat() + "-test")
    print(f"Geschrieben: {path}")
