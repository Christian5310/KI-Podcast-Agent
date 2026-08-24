"""Gemeinsamer Helfer: DeepSeek-Aufruf mit JSON-Antwort + Retry.

LLM-JSON ist gelegentlich leicht kaputt (kaputtes Escaping bei laengeren Strings).
Statt den ganzen Lauf abstuerzen zu lassen: 2x erneut versuchen, dann sauber
Klartext-Fehler statt kryptischem JSONDecodeError.
"""

import json

from openai import OpenAI

MAX_JSON_RETRIES = 2


def call_json(client: OpenAI, model: str, prompt: str, temperature: float = 0.3) -> dict:
    last_error = None
    for attempt in range(MAX_JSON_RETRIES + 1):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        raw = resp.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            last_error = exc
            print(f"[llm_json] Ungueltiges JSON (Versuch {attempt + 1}/{MAX_JSON_RETRIES + 1}): {exc}")

    raise RuntimeError(f"LLM lieferte {MAX_JSON_RETRIES + 1}x kein gueltiges JSON: {last_error}")
