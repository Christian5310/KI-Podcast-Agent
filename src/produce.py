"""Takt 2, Schritt 3: Produktion - Manuskript zu Audio (Zwei-Stimmen-TTS via ElevenLabs).

Aufbau je Folge: Musik-Sting -> Anmoderation ("Willkommen zum taeglichen KI Lab...")
-> Dialog mit kurzen Pausen zwischen den Sprecherwechseln (Huberman-Lab-Referenz:
ruhig, klar, kein Gehetze). Intro-Musik/-Stimme sind einmalig erzeugte, feste Assets
(src/assets.py) - werden wiederverwendet statt taeglich neu generiert.

Voice-IDs sind Platzhalter aus der ElevenLabs-Standardbibliothek - im ElevenLabs-
Dashboard (Voice Library) pruefen/durch eigene Wahl ersetzen (siehe .env).
"""

import io
import os
from pathlib import Path

import requests
from pydub import AudioSegment

from src.config import ELEVENLABS_API_KEY

OUT_DIR = Path(__file__).resolve().parent.parent / "out"
TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

VOICE_A = os.environ.get("ELEVENLABS_VOICE_A", "21m00Tcm4TlvDq8ikWAM")  # Platzhalter, in ElevenLabs pruefen
VOICE_B = os.environ.get("ELEVENLABS_VOICE_B", "pNInz6obpgDQGcFmaJgB")  # Platzhalter, in ElevenLabs pruefen
# Anmoderations-Stimme: maennlich, rau, "nicht zu nett" (Huberman-Lab-Referenz) - eigener Slot,
# unabhaengig von den Dialog-Stimmen A/B. Placeholder faellt auf VOICE_B zurueck; im ElevenLabs
# Voice-Library-Preview pruefen und via ELEVENLABS_VOICE_INTRO in .env durch eigene Wahl ersetzen.
VOICE_INTRO = os.environ.get("ELEVENLABS_VOICE_INTRO", VOICE_B)


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


def _mp3_bytes_to_segment(data: bytes) -> AudioSegment:
    return AudioSegment.from_file(io.BytesIO(data), format="mp3")


def produce_audio(script_text: str, episode_date: str) -> Path:
    """Baut Musik-Intro + Anmoderation + Dialog (mit Sprecherpausen) zu einer mp3 zusammen."""
    from src.assets import ensure_intro_assets

    lines = parse_dialogue(script_text)
    if not lines:
        raise ValueError("Kein verwertbarer Dialog im Manuskript gefunden (Format 'A: ...' / 'B: ...' erwartet)")

    music_path, voice_path = ensure_intro_assets()

    music = AudioSegment.from_file(music_path, format="mp3")
    voice = AudioSegment.from_file(voice_path, format="mp3")

    # Stimme setzt bei Sekunde 2 ein, ueber der (kurzen, ausklingenden) Musik.
    VOICE_START_MS = 2000
    bed_length = max(len(music), VOICE_START_MS + len(voice))
    intro = AudioSegment.silent(duration=bed_length)
    intro = intro.overlay(music, position=0)
    intro = intro.overlay(voice, position=VOICE_START_MS)

    final = intro + AudioSegment.silent(duration=700)

    for i, (speaker, text) in enumerate(lines, 1):
        voice_id = VOICE_A if speaker == "A" else VOICE_B
        segment = _mp3_bytes_to_segment(_tts_segment(text, voice_id))
        final += segment + AudioSegment.silent(duration=350)
        print(f"[produce] Segment {i}/{len(lines)} ({speaker}) geschrieben")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{episode_date}.mp3"
    final.export(out_path, format="mp3")

    return out_path


if __name__ == "__main__":
    from datetime import date

    sample = "A: Willkommen zur Testfolge.\nB: Schoen, dass du dabei bist."
    path = produce_audio(sample, date.today().isoformat() + "-test")
    print(f"Geschrieben: {path}")
