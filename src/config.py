"""Zentrale Konfiguration: Env-Variablen und die Quellenliste fuer Takt 1.

Quellen stammen aus quellen.md (Team-Recherche, verifiziert 24.08.2026).
Dies ist ein Startset fuer den Thinnest-Slice-Meilenstein (Phase 1) - bewusst
klein gehalten. Ausbau in Phase 2 (weitere Quellen aus quellen.md + Exa).

ACHTUNG: Zielgruppen-Frage noch offen (KI-Manager/Mittelstand vs. KI-Alltagsuser,
siehe Chat) - diese Liste ist ein neutraler Kompromiss-Vorschlag und wird nach
Klaerung ggf. angepasst.
"""

import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Windows-Konsolen-Codepage (cp1252) kann z.B. Emoji in Artikeltiteln nicht drucken und
# stuerzt sonst mit UnicodeEncodeError ab. UTF-8 erzwingen, unprintbare Zeichen ersetzen
# statt abzustuerzen.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com"  # offizieller, oeffentlicher Endpoint
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
EXA_API_KEY = os.environ.get("EXA_API_KEY", "")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    note: str


# Zielgruppe laut Entscheidung 24.08.2026: KI-Alltagsuser (nicht KI-Manager/Mittelstand) -
# daher VentureBeat (Enterprise) raus, The Verge (nutzerorientiert) rein.
# Phase 2 (24.08.2026): erweitert um weitere aus quellen.md verifizierte Quellen fuer mehr
# Themenbreite - Aufbereitungs-Agent (process.py) braucht genug Rohmaterial zum Cross-Checken.
FEEDS: list[Feed] = [
    Feed("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/", "breit, international"),
    Feed("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "sehr nutzerorientiert, Apps/Gadgets"),
    Feed("Ben's Bites", "https://www.bensbites.com/feed", "taeglicher, kompakter Ueberblick"),
    Feed("One Useful Thing", "https://oneusefulthing.substack.com/feed", "angewandt, verstaendlich (Ethan Mollick)"),
    Feed("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss", "Verbraucher-Blick, Kultur/Recht"),
    Feed("Simon Willison", "https://simonwillison.net/atom/everything/", "'ich hab's ausprobiert', praxisnah"),
    Feed("404 Media", "https://www.404media.co/rss/", "investigativ, gegen Langeweile/Wiederholung"),
    Feed("Hacker News", "https://news.ycombinator.com/rss", "Pulsmesser, Community-Diskussion"),
    # Entscheidung 24.08.2026: Reddit dazugenommen. Achtung: Reddit rate-limitet recht
    # aggressiv (429 bei zu dichten Anfragen, insb. von Cloud-IPs wie GitHub Actions) -
    # kein garantierter Treffer, aber durch die Fehler-Matrix in collect.py unkritisch,
    # wenn's mal ausfaellt.
    Feed("Reddit r/artificial", "https://www.reddit.com/r/artificial/.rss", "was bewegt echte Nutzer"),
    Feed("Reddit r/ChatGPT", "https://www.reddit.com/r/ChatGPT/.rss", "was bewegt echte Nutzer"),
]

MANUSCRIPT_TARGET_WORDS = (1400, 1600)
PODCAST_TARGET_MINUTES = 10
DELIVERY_DEADLINE_LOCAL = "08:00"
