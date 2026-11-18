"""Ask Gemini to review a pull request and post the result as a single PR comment.

Standard library only, so the workflow needs no install step. The review is advisory:
every error is reported as a workflow warning and the script exits with code 0.

Environment variables:
    GITHUB_TOKEN       token with pull-requests: write
    GITHUB_REPOSITORY  owner/repo (set by GitHub Actions)
    PR_NUMBER          pull request number
    GEMINI_API_KEY     Gemini API key (repository secret AI_REVIEW_API_KEY)
    GEMINI_MODEL       optional, overrides DEFAULT_MODEL

Run locally with --dry-run to print the comment instead of posting it.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

GITHUB_API = "https://api.github.com"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
DEFAULT_MODEL = "gemini-flash-latest"

# Hidden tag used to find and update our own comment instead of adding a new one each push
COMMENT_TAG = "<!-- kiniela-ai-review -->"

# Keep the request inside the free tier's per-minute token budget
MAX_DIFF_CHARS = 60_000
# Notebooks are huge JSON blobs with outputs; reviewing them wastes the whole budget
IGNORED_SUFFIXES = (".ipynb",)
RETRYABLE_STATUS = {429, 500, 503}
RETRY_DELAY_SECONDS = 20

REVIEW_PROMPT = """You review pull requests of Kiniela Predictor, a multiclass classifier
(6 classes, defined in src/kiniela/config.py) of football match results, with a Streamlit app.

Project rules (from AGENTS.md):
- Reusable code lives in src/kiniela/; notebooks and the app call it, they do not duplicate it.
- No data leakage: historical features use only matches played before the predicted one.
- Every seed, split and model uses RANDOM_STATE from config.py.
- The meaning of `target` and the class thresholds do not change silently.
- No secrets, .env, datasets or trained models are committed.
- Tests are never skipped or deleted to make the suite pass; behaviour changes come with tests.
- Code, names, comments and commits in English; documentation in Spanish.

Review only the diff you receive. Answer in Markdown, in Spanish, in at most 300 words:
1. One line saying what the PR does.
2. Problems, most serious first, each with its file and why it matters. Write "Ninguno" if none.
3. Optional suggestions.
Do not praise, do not restate the diff and do not invent code that is not in it."""


def warn(message: str) -> None:
    """Show a warning in the workflow summary without failing the job."""
    print(f"::warning title=AI review skipped::{message}")


def http(url: str, token: str, *, method: str = "GET", payload: dict | None = None,
         accept: str = "application/vnd.github+json") -> bytes:
    """Send a request with a bearer token and return the raw response body."""
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def filter_diff(diff: str) -> str:
    """Remove the file sections that are not worth reviewing (see IGNORED_SUFFIXES)."""
    # Split before each "diff --git" header so every section keeps its own header line
    sections = re.split(r"(?m)^(?=diff --git )", diff)
    kept = [s for s in sections if not s.partition("\n")[0].endswith(IGNORED_SUFFIXES)]
    return "".join(kept)


def ask_gemini(diff: str, api_key: str, model: str) -> str:
    """Return Gemini's review of the diff, retrying once if the service is busy."""
    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 8_000,
        "reasoning_effort": "low",
        "messages": [
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": f"```diff\n{diff}\n```"},
        ],
    }
    for attempt in (1, 2):
        try:
            raw = http(GEMINI_URL, api_key, method="POST", payload=payload,
                       accept="application/json")
            break
        except urllib.error.HTTPError as error:
            if attempt == 2 or error.code not in RETRYABLE_STATUS:
                raise
            print(f"Gemini answered HTTP {error.code}; retrying in {RETRY_DELAY_SECONDS}s.")
            time.sleep(RETRY_DELAY_SECONDS)
    return json.loads(raw)["choices"][0]["message"]["content"].strip()


def build_comment(review: str, model: str, truncated: bool) -> str:
    """Wrap the review with the hidden tag and the advisory footer."""
    note = (
        f"\n\n> El diff superaba {MAX_DIFF_CHARS:,} caracteres: solo se ha revisado la primera parte."
        if truncated else ""
    )
    return (
        f"{COMMENT_TAG}\n## AI review\n\n{review}{note}\n\n---\n"
        f"*Revisión automática con `{model}`. Solo orienta: no aprueba ni bloquea el PR.*"
    )


def post_or_update(repo: str, number: str, token: str, body: str) -> None:
    """Edit our previous comment if it exists, otherwise create it."""
    comments_url = f"{GITHUB_API}/repos/{repo}/issues/{number}/comments"
    comments = json.loads(http(f"{comments_url}?per_page=100", token))
    previous = next((c for c in comments if COMMENT_TAG in (c.get("body") or "")), None)
    if previous:
        http(previous["url"], token, method="PATCH", payload={"body": body})
    else:
        http(comments_url, token, method="POST", payload={"body": body})


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    number = os.environ.get("PR_NUMBER", "")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model = os.environ.get("GEMINI_MODEL") or DEFAULT_MODEL

    if not (token and repo and number):
        warn("GITHUB_TOKEN, GITHUB_REPOSITORY and PR_NUMBER are required.")
        return
    if not api_key:
        warn("The AI_REVIEW_API_KEY repository secret is not set.")
        return

    try:
        diff = http(f"{GITHUB_API}/repos/{repo}/pulls/{number}", token,
                    accept="application/vnd.github.diff").decode("utf-8", "replace")
        diff = filter_diff(diff)
        if not diff.strip():
            print("Nothing to review.")
            return
        truncated = len(diff) > MAX_DIFF_CHARS
        review = ask_gemini(diff[:MAX_DIFF_CHARS], api_key, model)
        comment = build_comment(review, model, truncated)
        if "--dry-run" in sys.argv:
            print(comment)
            return
        post_or_update(repo, number, token, comment)
        print("AI review posted.")
    except Exception as error:  # noqa: BLE001 - the review must never break the pipeline
        warn(f"{type(error).__name__}: {error}")


if __name__ == "__main__":
    main()
