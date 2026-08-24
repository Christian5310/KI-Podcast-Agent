"""Feste Intro-Assets: Musik-Sting + Anmoderation. Werden EINMAL erzeugt und dann
wiederverwendet statt jeden Tag neu (Kriterium 6 - keine wiederkehrenden Kosten fuer
immer denselben Text).

python -m src.assets  -> erzeugt assets/intro_music.mp3 und assets/intro_voice.mp3
"""

import wave
from pathlib import Path

import numpy as np
from pydub import AudioSegment

from src.produce import ELEVENLABS_API_KEY, VOICE_INTRO, _tts_segment

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
INTRO_TEXT = (
    "Willkommen zum täglichen KI Lab, dem täglichen KI-Podcast mit aktueller Info "
    "rund um das Thema KI."
)


def _synth_pad(freqs: list[float], duration_s: float, sample_rate: int = 44100) -> np.ndarray:
    """Warmer, ruhiger Ambient-Pad-Akkord (Huberman-Lab-artig: schlicht, dezent)."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    signal = np.zeros_like(t)
    for f in freqs:
        # leichtes Detuning zweier Sinustoene pro Note fuer einen weichen Chorus-Klang
        signal += np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * (f * 1.003) * t)
    signal /= len(freqs)

    # Attack/Release-Huelle statt hartem Ein-/Ausblenden. Kurz gehalten: klingt schon
    # ab ~1.6s aus, so dass die Stimme (setzt bei Sekunde 2 ein) auf abschwellender
    # Musik startet, statt auf den vollen Akkord zu warten.
    attack = int(0.35 * sample_rate)
    release = int(1.5 * sample_rate)
    envelope = np.ones_like(signal)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)

    return signal * envelope * 0.18  # dezente Lautstaerke


def make_intro_music(path: Path, duration_s: float = 3.1) -> None:
    freqs = [130.81, 196.00, 261.63, 329.63]  # C3, G3, C4, E4 - ruhiger, offener Akkord
    audio = _synth_pad(freqs, duration_s)
    audio_int16 = np.int16(np.clip(audio, -1, 1) * 32767)

    wav_path = path.with_suffix(".wav")
    with wave.open(str(wav_path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(44100)
        f.writeframes(audio_int16.tobytes())

    AudioSegment.from_wav(wav_path).export(path, format="mp3")
    wav_path.unlink()
    print(f"[assets] Musik-Sting geschrieben: {path}")


def make_intro_voice(path: Path) -> None:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY fehlt in .env")
    audio_bytes = _tts_segment(INTRO_TEXT, VOICE_INTRO)
    path.write_bytes(audio_bytes)
    print(f"[assets] Intro-Stimme geschrieben: {path}")


def ensure_intro_assets() -> tuple[Path, Path]:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    music_path = ASSETS_DIR / "intro_music.mp3"
    voice_path = ASSETS_DIR / "intro_voice.mp3"
    if not music_path.exists():
        make_intro_music(music_path)
    if not voice_path.exists():
        make_intro_voice(voice_path)
    return music_path, voice_path


if __name__ == "__main__":
    ensure_intro_assets()
