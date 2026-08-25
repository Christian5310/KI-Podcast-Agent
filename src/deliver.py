"""C3 (Pflicht): minimale Zustellung - oeffentliche Seite ohne Login, die den
neuesten Podcast abspielt, aeltere findet, Quellen zeigt. Erzeugt index.html +
einen podcast-kompatiblen RSS-Feed (rss.xml) aus den Supabase-Daten, schreibt
beides nach site/ - wird von GitHub Pages ausgeliefert (siehe .github/workflows).

Kein eigener Server, keine Datenbank-Abfrage zur Laufzeit noetig: die Seite ist
bei jedem Lauf frisch generiertes, statisches HTML.
"""

from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

from src.db import all_episodes, episode_topics, get_client

SITE_DIR = Path(__file__).resolve().parent.parent / "site"
SITE_URL = "https://christian5310.github.io/KI-Podcast-Agent"  # ggf. anpassen (GitHub Pages URL)
FORMAT_LABELS = {"daily": "Tagesfolge", "monday_recap": "Wochenend-Rückblick", "friday_overview": "Wochenüberblick"}


def _episode_title(ep: dict) -> str:
    d = datetime.fromisoformat(ep["episode_date"])
    return f"KI Lab – {d.strftime('%d.%m.%Y')} ({FORMAT_LABELS.get(ep['format'], ep['format'])})"


def build_site() -> None:
    client = get_client()
    episodes = [e for e in all_episodes(client) if e.get("audio_url")]

    SITE_DIR.mkdir(parents=True, exist_ok=True)
    _write_index(episodes, client)
    _write_rss(episodes)
    print(f"[deliver] {len(episodes)} Folgen -> site/index.html + site/rss.xml")


def _write_index(episodes: list[dict], client) -> None:
    cards = []
    for i, ep in enumerate(episodes):
        topics = episode_topics(client, ep.get("topic_ids") or [])
        sources_html = "".join(
            f'<li><a href="{escape(t["source_urls"][0])}" target="_blank" rel="noopener">{escape(t["title"])}</a></li>'
            for t in topics if t.get("source_urls")
        )
        latest_class = " latest" if i == 0 else ""
        cards.append(f"""
        <article class="episode{latest_class}">
          <h2>{escape(_episode_title(ep))}</h2>
          <audio controls preload="none" src="{escape(ep['audio_url'])}"></audio>
          <p class="meta">{ep.get('word_count', '?')} Wörter</p>
          <details><summary>Quellen</summary><ul>{sources_html}</ul></details>
        </article>""")

    html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>KI Lab – der tägliche KI-Podcast</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="KI Lab" href="rss.xml">
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  h1 {{ font-size: 1.6rem; }}
  .episode {{ border-bottom: 1px solid #ddd; padding: 1.2rem 0; }}
  .episode.latest {{ border: 2px solid #34215D; border-radius: 8px; padding: 1rem; background: #faf9ff; }}
  audio {{ width: 100%; margin: 0.5rem 0; }}
  .meta {{ color: #666; font-size: 0.85rem; }}
  details summary {{ cursor: pointer; color: #34215D; }}
</style>
</head>
<body>
<h1>🎙️ KI Lab – der tägliche KI-Podcast</h1>
<p>Automatisch produziert, jeden Werktag vor 8 Uhr. <a href="rss.xml">RSS-Feed</a></p>
{"".join(cards) or "<p>Noch keine Folge veröffentlicht.</p>"}
</body>
</html>"""
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")


def _write_rss(episodes: list[dict]) -> None:
    items = []
    for ep in episodes:
        pub_date = format_datetime(
            datetime.fromisoformat(ep["episode_date"]).replace(tzinfo=timezone.utc)
        )
        items.append(f"""
    <item>
      <title>{escape(_episode_title(ep))}</title>
      <enclosure url="{escape(ep['audio_url'])}" type="audio/mpeg"/>
      <guid>{escape(ep['audio_url'])}</guid>
      <pubDate>{pub_date}</pubDate>
    </item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>KI Lab</title>
  <link>{SITE_URL}</link>
  <description>Der tägliche KI-Podcast – automatisch produziert, jeden Werktag vor 8 Uhr.</description>
  <language>de-de</language>
  {"".join(items)}
</channel>
</rss>"""
    (SITE_DIR / "rss.xml").write_text(rss, encoding="utf-8")


if __name__ == "__main__":
    build_site()
