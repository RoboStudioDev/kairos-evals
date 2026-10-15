"""Calling Gemini on Google Cloud (Vertex AI), the same way the Kairos server does.

No extra packages: the request is plain HTTPS, and the sign-in comes from the Google Cloud
command-line tool (``gcloud auth print-access-token``), so nothing secret is stored in this repo.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request

ENDPOINT = (
    "https://aiplatform.googleapis.com/v1/projects/{project}/locations/global"
    "/publishers/google/models/{model}:{method}"
)


class GeminiError(RuntimeError):
    pass


def _gcloud(*args: str) -> str:
    try:
        done = subprocess.run(["gcloud", *args], capture_output=True, text=True, timeout=60)
    except FileNotFoundError as exc:
        raise GeminiError("The Google Cloud command-line tool (gcloud) isn't installed.") from exc
    if done.returncode != 0:
        raise GeminiError(f"gcloud {' '.join(args)} failed: {done.stderr.strip()[:300]}")
    return done.stdout.strip()


def access_token() -> str:
    return _gcloud("auth", "print-access-token")


def project_id(explicit: str | None = None) -> str:
    """--project, else KAIROS_EVALS_PROJECT, else gcloud's default project."""
    project = explicit or os.environ.get("KAIROS_EVALS_PROJECT") or _gcloud("config", "get-value", "project")
    if not project:
        raise GeminiError("No Google Cloud project. Pass --project or set KAIROS_EVALS_PROJECT.")
    return project


def _post(url: str, token: str, body: dict, attempts: int = 3) -> dict:
    data = json.dumps(body).encode("utf-8")
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:400]
            if exc.code in (429, 500, 503) and attempt < attempts:
                time.sleep(5 * attempt)
                continue
            raise GeminiError(f"Vertex AI answered {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            if attempt < attempts:
                time.sleep(5 * attempt)
                continue
            raise GeminiError(f"Couldn't reach Vertex AI: {exc.reason}") from exc
    raise GeminiError("unreachable")


def count_tokens(prompt: str, model: str, project: str, token: str) -> int:
    """Google's token counter. Free: it reads the prompt, it doesn't run the model."""
    url = ENDPOINT.format(project=project, model=model, method="countTokens")
    out = _post(url, token, {"contents": [{"role": "user", "parts": [{"text": prompt}]}]})
    return int(out.get("totalTokens", 0))


def generate(prompt: str, model: str, project: str, token: str, generation: dict) -> dict:
    """One model call. Costs money. Returns the text, token counts and timing."""
    url = ENDPOINT.format(project=project, model=model, method="generateContent")
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": generation}
    started = time.monotonic()
    out = _post(url, token, body)
    seconds = time.monotonic() - started
    cand = (out.get("candidates") or [{}])[0]
    # Like the server: join every text part.
    text = "".join(p.get("text", "") for p in (cand.get("content") or {}).get("parts", []) if isinstance(p.get("text"), str)).strip()
    usage = out.get("usageMetadata") or {}
    return {
        "text": text,
        "finishReason": cand.get("finishReason"),
        "modelVersion": out.get("modelVersion"),
        "seconds": round(seconds, 2),
        "inputTokens": int(usage.get("promptTokenCount", 0)),
        # Thinking tokens are billed as output.
        "outputTokens": int(usage.get("candidatesTokenCount", 0)) + int(usage.get("thoughtsTokenCount", 0)),
        "thinkingTokens": int(usage.get("thoughtsTokenCount", 0)),
    }
