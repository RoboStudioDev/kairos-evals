"""What a model call costs, in US dollars per million tokens.

From the Kairos server's own notes (functions/aiModels.js and index.js, 2026-10-14). Check
Google's Vertex AI pricing page before trusting them; update this table when they change.
Thinking tokens are billed at the output rate.
"""

from __future__ import annotations

from datetime import date

# model: [(last day this price applies, or None for "from then on"), input $/1M, output $/1M]
PRICES = {
    "gemini-4-argon": [(date(2026, 11, 30), 2.00, 10.00), (None, 4.00, 20.00)],
    # Kairos lists $1.50 / $7.50 as 3.8 Flash's price once launch offers end; used as the upper bound.
    "gemini-3.8-flash": [(None, 1.50, 7.50)],
}


def rates(model: str, day: date | None = None) -> tuple[float, float]:
    day = day or date.today()
    for until, price_in, price_out in PRICES[model]:
        if until is None or day <= until:
            return price_in, price_out
    raise KeyError(model)


def cost(model: str, input_tokens: int, output_tokens: int, day: date | None = None) -> float:
    price_in, price_out = rates(model, day)
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000
