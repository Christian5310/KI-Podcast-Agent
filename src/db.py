"""Supabase-Client und Abfragen fuer das Themen-Gedaechtnis (A5).

Schema: supabase/schema.sql. Braucht SUPABASE_URL/SUPABASE_KEY in .env -
bis das Projekt feststeht (siehe Chat), ist dieses Modul nicht lauffaehig,
aber schon vollstaendig verdrahtet.
"""

from datetime import date, datetime, timedelta, timezone

from supabase import Client, create_client

from src.config import SUPABASE_KEY, SUPABASE_URL


def get_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("SUPABASE_URL/SUPABASE_KEY fehlen in .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def recent_topics(client: Client, days: int = 14) -> list[dict]:
    """Fuer den Dedupe-/Cross-Check-Schritt (A2/A4): Themen der letzten N Tage."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    res = client.table("topics").select("*").gte("last_updated", cutoff).execute()
    return res.data


def insert_topic(client: Client, title: str, summary: str, source_urls: list[str],
                  parent_topic_id: str | None = None, whats_new: str | None = None) -> dict:
    row = {
        "title": title,
        "summary": summary,
        "source_urls": source_urls,
        "parent_topic_id": parent_topic_id,
        "whats_new": whats_new,
    }
    res = client.table("topics").insert(row).execute()
    return res.data[0]


def mark_topics_used(client: Client, topic_ids: list[str], episode_date: date) -> None:
    client.table("topics").update({"status": "used", "used_in_episode": episode_date.isoformat()}).in_(
        "id", topic_ids
    ).execute()


def insert_episode(client: Client, episode_date: date, script_text: str, format_: str = "daily") -> dict:
    row = {
        "episode_date": episode_date.isoformat(),
        "format": format_,
        "script_text": script_text,
        "word_count": len(script_text.split()),
    }
    res = client.table("episodes").insert(row).execute()
    return res.data[0]


def last_episode() -> dict | None:
    client = get_client()
    res = client.table("episodes").select("*").order("episode_date", desc=True).limit(1).execute()
    return res.data[0] if res.data else None
