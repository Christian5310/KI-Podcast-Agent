"""Kriterium 6: Kostentransparenz. Preise Stand 24.08.2026, per Skill/Doku geprueft
(nicht aus dem Training geraten - Preise aendern sich, siehe Hinweise unten).

Claude Sonnet 5: Einfuehrungspreis $2.00/$10.00 pro 1M Tokens (In/Out) NUR bis
2026-08-31, danach $3.00/$15.00 - PREISE_SONNET5 hat beide, waehlt automatisch
nach Datum.

DeepSeek: "deepseek-chat" ist laut offizieller Doku abgekuendigt (seit 24.07.2026),
funktioniert aber noch inoffiziell. Wir nutzen bewusst den aktuell dokumentierten
Namen deepseek-v4-flash. Peak-Zeiten (01:00-04:00 und 06:00-10:00 UTC) kosten
doppelt - relevant, weil unser Morgenlauf laut Plan genau in dieses Fenster faellt.

USD->EUR ist ein fester Naeherungswert (kein Live-Kurs), fuer Kostentransparenz
auf +/- ein paar Prozent genau genug.
"""

from datetime import date, datetime, timezone

USD_TO_EUR = 0.92  # Naeherung, kein Live-Kurs

SONNET5_INTRO_END = date(2026, 8, 31)


def _sonnet5_rates() -> tuple[float, float]:
    """($/1M input, $/1M output) - Einfuehrungspreis nur bis 31.08.2026."""
    if date.today() <= SONNET5_INTRO_END:
        return 2.00, 10.00
    return 3.00, 15.00


def _is_peak_utc() -> bool:
    hour = datetime.now(timezone.utc).hour
    return (1 <= hour < 4) or (6 <= hour < 10)


def _deepseek_flash_rates() -> tuple[float, float]:
    """($/1M input bei Cache-Miss, $/1M output) - konservativ (kein Cache-Hit
    angenommen, da wir das aus der OpenAI-kompatiblen Antwort nicht sauber
    auslesen); Peak/Off-Peak automatisch nach UTC-Uhrzeit."""
    peak = _is_peak_utc()
    return (0.44, 1.32) if peak else (0.22, 0.66)


PRICING = {
    "claude-sonnet-5": _sonnet5_rates,
    "deepseek-v4-flash": _deepseek_flash_rates,
}


def estimate_cost_eur(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in PRICING:
        raise ValueError(f"Kein Preis hinterlegt fuer Modell {model!r} - costs.py ergaenzen")
    rate_in, rate_out = PRICING[model]()
    usd = (input_tokens / 1_000_000) * rate_in + (output_tokens / 1_000_000) * rate_out
    return round(usd * USD_TO_EUR, 6)
