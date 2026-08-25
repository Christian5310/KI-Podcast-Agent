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


def log_usage(client: Client, agent: str, model: str, input_tokens: int, output_tokens: int,
              episode_date: date | None = None, note: str | None = None) -> None:
    """Kriterium 6: jeder Modellaufruf wird mit Kosten protokolliert."""
    from src.costs import estimate_cost_eur

    client.table("usage_log").insert(
        {
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_eur": estimate_cost_eur(model, input_tokens, output_tokens),
            "episode_date": episode_date.isoformat() if episode_date else None,
            "note": note,
        }
    ).execute()


def cost_summary(client: Client, since: date | None = None) -> list[dict]:
    """Fuer die Kostenaussage am Mittwoch: Summe je Agent + Modell."""
    query = client.table("usage_log").select("agent, model, input_tokens, output_tokens, cost_eur")
    if since:
        query = query.gte("created_at", since.isoformat())
    rows = query.execute().data

    summary: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (r["agent"], r["model"])
        entry = summary.setdefault(key, {"agent": r["agent"], "model": r["model"], "calls": 0,
                                          "input_tokens": 0, "output_tokens": 0, "cost_eur": 0.0})
        entry["calls"] += 1
        entry["input_tokens"] += r["input_tokens"]
        entry["output_tokens"] += r["output_tokens"]
        entry["cost_eur"] += float(r["cost_eur"])
    return sorted(summary.values(), key=lambda e: -e["cost_eur"])


def upload_audio(client: Client, local_path, episode_date: date) -> str:
    """C2/C3: Audiodatei oeffentlich erreichbar ablegen (Supabase Storage, public bucket).
    Gibt die stabile oeffentliche URL zurueck."""
    object_path = f"{episode_date.isoformat()}.mp3"
    with open(local_path, "rb") as f:
        client.storage.from_("audio").upload(
            object_path, f, {"content-type": "audio/mpeg", "upsert": "true"}
        )
    return client.storage.from_("audio").get_public_url(object_path)


def all_episodes(client: Client, limit: int = 60) -> list[dict]:
    """Fuer die Zustellung (C3): alle Folgen, neueste zuerst."""
    res = (
        client.table("episodes")
        .select("episode_date, format, audio_url, word_count, topic_ids")
        .order("episode_date", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data


def episode_topics(client: Client, topic_ids: list[str]) -> list[dict]:
    if not topic_ids:
        return []
    res = client.table("topics").select("title, source_urls").in_("id", topic_ids).execute()
    return res.data


def week_block_counts(client: Client) -> dict[str, int]:
    """Fuer die Themenblock-Regel (Entscheidungstabelle Punkt 1): wie oft kam welcher
    Themenblock diese Woche (Mo-heute) schon in einer Folge vor."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    episodes = (
        client.table("episodes")
        .select("topic_ids")
        .gte("episode_date", monday.isoformat())
        .execute()
        .data
    )
    all_topic_ids = [tid for ep in episodes for tid in (ep.get("topic_ids") or [])]
    if not all_topic_ids:
        return {}

    topics = client.table("topics").select("themenblock").in_("id", all_topic_ids).execute().data
    counts: dict[str, int] = {}
    for t in topics:
        block = t.get("themenblock")
        if block:
            counts[block] = counts.get(block, 0) + 1
    return counts


def week_topics_summary(client: Client, before: date) -> str:
    """B5 (Freitag-Sonderformat): Themen dieser Woche (Mo bis vor 'before'), formatiert
    fuer den Wochenueberblick-Prompt - der soll NICHT nacherzaehlen, sondern einordnen."""
    monday = before - timedelta(days=before.weekday())
    episodes = (
        client.table("episodes")
        .select("episode_date, topic_ids")
        .gte("episode_date", monday.isoformat())
        .lt("episode_date", before.isoformat())
        .order("episode_date")
        .execute()
        .data
    )
    if not episodes:
        return ""

    lines = []
    for ep in episodes:
        topic_ids = ep.get("topic_ids") or []
        if not topic_ids:
            continue
        topics = client.table("topics").select("title, whats_new").in_("id", topic_ids).execute().data
        d = datetime.fromisoformat(ep["episode_date"]).strftime("%A, %d.%m.")
        lines.append(f"{d}:")
        for t in topics:
            entry = f"  - {t['title']}"
            if t.get("whats_new"):
                entry += f" (Update: {t['whats_new']})"
            lines.append(entry)
    return "\n".join(lines)


def repetition_metric(client: Client, n_episodes: int = 7) -> dict:
    """D7: leichtgewichtige Kennzahl fuer den Kriterium-2/3-Nachweis am Mittwoch - wie
    stark ueberschneiden sich die Themen-Titel benachbarter Folgen (Jaccard auf
    Woertern). Niedrig = echte Themenvielfalt statt Wiederholung. Kein Anspruch auf
    Praezision, nur ein schneller, nachvollziehbarer Beleg."""
    import re

    episodes = (
        client.table("episodes")
        .select("episode_date, topic_ids")
        .order("episode_date", desc=True)
        .limit(n_episodes)
        .execute()
        .data
    )

    per_episode = []
    for ep in episodes:
        topic_ids = ep.get("topic_ids") or []
        if not topic_ids:
            continue
        topics = client.table("topics").select("title").in_("id", topic_ids).execute().data
        words = set(re.findall(r"\w+", " ".join(t["title"] for t in topics).lower()))
        per_episode.append((ep["episode_date"], words))

    pairs = []
    for i in range(len(per_episode) - 1):
        date_a, words_a = per_episode[i]
        date_b, words_b = per_episode[i + 1]
        if not words_a or not words_b:
            continue
        overlap = len(words_a & words_b) / len(words_a | words_b)
        pairs.append({"from": date_b, "to": date_a, "overlap": round(overlap, 3)})

    avg = round(sum(p["overlap"] for p in pairs) / len(pairs), 3) if pairs else 0.0
    return {"episodes_compared": len(per_episode), "avg_overlap": avg, "pairs": pairs}


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


def episode_cost(client: Client, episode_date: date) -> tuple[float, dict]:
    """Summe + Aufschluesselung nach Agent fuer genau diese Folge (Manuskript+Faktencheck-
    Anteil - der Aufbereitungs-Agent laeuft unabhaengig ueber den Tag, siehe Chat)."""
    rows = (
        client.table("usage_log")
        .select("agent, model, input_tokens, output_tokens, cost_eur")
        .eq("episode_date", episode_date.isoformat())
        .execute()
        .data
    )
    total = sum(float(r["cost_eur"]) for r in rows)
    by_agent: dict[str, float] = {}
    for r in rows:
        by_agent[r["agent"]] = by_agent.get(r["agent"], 0.0) + float(r["cost_eur"])
    return round(total, 6), by_agent


def insert_episode(client: Client, episode_date: date, script_text: str, format_: str = "daily",
                    audio_url: str | None = None, topic_ids: list[str] | None = None) -> dict:
    cost_eur, by_agent = episode_cost(client, episode_date)
    row = {
        "episode_date": episode_date.isoformat(),
        "format": format_,
        "script_text": script_text,
        "word_count": len(script_text.split()),
        "cost_eur": cost_eur,
        "model_usage": by_agent,
        "audio_url": audio_url,
        "topic_ids": topic_ids,
    }
    res = client.table("episodes").upsert(row, on_conflict="episode_date").execute()
    return res.data[0]


def last_episode() -> dict | None:
    client = get_client()
    res = client.table("episodes").select("*").order("episode_date", desc=True).limit(1).execute()
    return res.data[0] if res.data else None
