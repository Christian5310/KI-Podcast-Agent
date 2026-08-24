"""Gemeinsamer Helfer: DeepSeek-Aufruf mit JSON-Antwort + Retry.

LLM-JSON ist gelegentlich leicht kaputt (kaputtes Escaping bei laengeren Strings).
Statt den ganzen Lauf abstuerzen zu lassen: 2x erneut versuchen, dann sauber
Klartext-Fehler statt kryptischem JSONDecodeError.
"""

import json

from openai import OpenAI

MAX_JSON_RETRIES = 2


def call_json(
    client: OpenAI, model: str, prompt: str, temperature: float = 0.3,
    *, agent: str = "", db_client=None, episode_date=None,
) -> dict:
    """agent/db_client/episode_date optional: wenn db_client gesetzt ist, wird jeder
    Aufruf (auch fehlgeschlagene JSON-Versuche - die kosten auch echtes Geld) sofort
    in usage_log geschrieben (Kriterium 6)."""
    last_error = None
    for attempt in range(MAX_JSON_RETRIES + 1):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        if db_client is not None:
            from src.db import log_usage

            log_usage(
                db_client, agent, model,
                resp.usage.prompt_tokens, resp.usage.completion_tokens,
                episode_date=episode_date,
            )

        raw = resp.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            last_error = exc
            print(f"[llm_json] Ungueltiges JSON (Versuch {attempt + 1}/{MAX_JSON_RETRIES + 1}): {exc}")

    raise RuntimeError(f"LLM lieferte {MAX_JSON_RETRIES + 1}x kein gueltiges JSON: {last_error}")
