"""Supabase-Client und Abfragen fuer das Themen-Gedaechtnis (A5).

Schema: supabase/schema.sql (+ Migration add_scoring_and_verification).
Projekt: KI Podcast Agent (ylvpovjrloqpjypcfkya, eu-central-1).
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


def insert_topic(client: Client, topic: dict) -> dict:
    """Nimmt direkt das Ergebnis-Dict aus process.process_items()."""
    res = client.table("topics").insert(topic).execute()
    return res.data[0]


def candidate_topics(client: Client, limit: int = 30) -> list[dict]:
    """Fuer die Auswahl (select.py): unverbrauchte Themen, nach Score sortiert."""
    res = (
        client.table("topics")
        .select("*")
        .eq("status", "candidate")
        .order("total_score", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


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
