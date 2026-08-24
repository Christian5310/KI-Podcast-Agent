-- Podcast-Gedaechtnis (A5): Themen mit Quelle, Datum, Status, Vorgaenger-Referenz.
-- Anwenden sobald das Supabase-Projekt feststeht (siehe Chat).

create table if not exists topics (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    summary text not null,
    -- eine oder mehrere Quellen-URLs je Thema (Kriterium 4/5: aufrufbare Quelle)
    source_urls text[] not null,
    first_seen timestamptz not null default now(),
    last_updated timestamptz not null default now(),
    -- 'candidate' -> 'used' -> ggf. 'superseded' bei echter Fortsetzung
    status text not null default 'candidate' check (status in ('candidate', 'used', 'superseded')),
    -- verweist auf die Vorgaenger-Meldung, falls dies eine Fortsetzung ist (A4)
    parent_topic_id uuid references topics(id),
    -- was ist neu an dieser Fortsetzung, explizit festgehalten (A4)
    whats_new text,
    used_in_episode date
);

create index if not exists idx_topics_last_updated on topics(last_updated);
create index if not exists idx_topics_status on topics(status);

create table if not exists episodes (
    id uuid primary key default gen_random_uuid(),
    episode_date date not null unique,
    format text not null default 'daily' check (format in ('daily', 'monday_recap', 'friday_overview')),
    script_text text,
    audio_url text,
    word_count int,
    topic_ids uuid[],
    -- Kriterium 6: Kostentransparenz je Lauf
    cost_eur numeric(10, 4),
    model_usage jsonb,
    factcheck_passed boolean,
    created_at timestamptz not null default now()
);
