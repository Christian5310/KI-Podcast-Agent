"""Zentrale Konfiguration: Env-Variablen und die Quellenliste fuer Takt 1.

Quellen stammen aus quellen.md (Team-Recherche, verifiziert 24.08.2026).
Dies ist ein Startset fuer den Thinnest-Slice-Meilenstein (Phase 1) - bewusst
klein gehalten. Ausbau in Phase 2 (weitere Quellen aus quellen.md + Exa).

ACHTUNG: Zielgruppen-Frage noch offen (KI-Manager/Mittelstand vs. KI-Alltagsuser,
siehe Chat) - diese Liste ist ein neutraler Kompromiss-Vorschlag und wird nach
Klaerung ggf. angepasst.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    note: str


# Startset Phase 1 (Thinnest Slice) - alle Feeds am 24.08.2026 live verifiziert (HTTP 200).
FEEDS: list[Feed] = [
    Feed("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "breit, international"),
    Feed("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "Enterprise/Business-Blick"),
    Feed("Ben's Bites", "https://www.bensbites.com/feed", "taeglicher, kompakter Ueberblick"),
    Feed("One Useful Thing", "https://oneusefulthing.substack.com/feed", "angewandt, managementnah (Ethan Mollick)"),
]

MANUSCRIPT_TARGET_WORDS = (1400, 1600)
PODCAST_TARGET_MINUTES = 10
DELIVERY_DEADLINE_LOCAL = "08:00"
