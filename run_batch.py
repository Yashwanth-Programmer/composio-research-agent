import concurrent.futures
import csv
import json
import os
import re
import sys
import time
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Config & Setup
# ---------------------------------------------------------------------------
INPUT_CSV = "apps.csv"          # columns: app_name, hint, category
OUTPUT_JSONL = "results.jsonl"  # one JSON object per line, appended as we go
DELAY_SECONDS = 5               # Buffer to respect Gemini free tier RPM
MAX_RETRIES = 4
CALL_TIMEOUT_SECONDS = 180      # timeout per app search

# Set to current supported 2026 model
MODEL = "gemini-3.5-flash-lite"
USER_ID = "research_agent_v1"

# Initialize Clients gracefully
try:
    composio_client = Composio(provider=GeminiProvider())
    gemini_client = genai.Client() # Requires GEMINI_API_KEY in env
    
    # Setup Composio Toolset
    session = composio_client.create(user_id=USER_ID, toolkits=["composio_search"])
    COMPOSIO_TOOLS = session.tools()
except Exception as e:
    print(f"Error during initialization: {e}")
    print("Ensure COMPOSIO_API_KEY and GEMINI_API_KEY are set in your environment or terminal.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Research Agent Logic
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a research agent investigating a software app for API/agent buildability.
Use web search tools available to you to find real, current information.
Given an app name and hint URL, find:
- one_liner: what app does, one line
- auth_methods: list, e.g. ["OAuth2"], ["API key"], etc
- self_serve: "self-serve" or "gated"
- gate_reason: if gated, why (paid plan / admin approval / contact-sales / none)
- api_surface: "REST" / "GraphQL" / "both" / "none"
- api_breadth: "narrow" / "broad"
- mcp_exists: true or false
- buildability: "yes" / "no" / "partial"
- blocker: main blocker if not buildable, else ""
- evidence_url: exact docs URL you found this from
- confidence: 0.0-1.0

When done, respond with ONLY a JSON object, no markdown fences, no prose."""

def research_app(app_name: str, hint: str, category: str) -> dict:
    prompt = f"{SYSTEM_PROMPT}\n\nApp: {app_name}\nHint: {hint}\nCategory: {category}\nResearch it now."

    config = types.GenerateContentConfig(tools=COMPOSIO_TOOLS)
    chat = gemini_client.chats.create(model=MODEL, config=config)
    
    # Automatic Function Calling handles the tool loop dynamically
    response = chat.send_message(prompt) 

    text = response.text or ""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback cleanup if the model hallucinates markdown fences
        cleaned = text.strip().strip("`").replace("json\n", "", 1)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"app": app_name, "notes": "PARSE_FAILED", "raw": text}

# ---------------------------------------------------------------------------
# Batch Processing & Retry Logic
# ---------------------------------------------------------------------------
def already_done(output_path):
    """Return set of app names already processed, so reruns skip them."""
    done = set()
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    name = row.get("_app_name") or row.get("app")
                    if name:
                        done.add(name)
                except json.JSONDecodeError:
                    continue
    return done

def extract_retry_delay(err):
    """Pull suggested retry delay out of rate limit errors."""
    msg = str(err)
    match = re.search(r"'retryDelay':\s*'(\d+)s'", msg)
    if match:
        return int(match.group(1)) + 2
    return None

def call_with_timeout(app_name, hint, category, timeout):
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = ex.submit(research_app, app_name, hint, category)
    try:
        result = future.result(timeout=timeout)
        ex.shutdown(wait=False)
        return result
    except concurrent.futures.TimeoutError:
        ex.shutdown(wait=False)
        raise RuntimeError(f"Timed out after {timeout}s")

def run_with_retries(app_name, hint, category):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = call_with_timeout(app_name, hint, category, CALL_TIMEOUT_SECONDS)
            return result
        except Exception as e:
            last_err = e
            suggested = extract_retry_delay(e)
            wait = suggested if suggested else DELAY_SECONDS * attempt * 2
            print(f"   [retry {attempt}/{MAX_RETRIES}] {app_name} failed: {e}. Waiting {wait}s...")
            time.sleep(wait)
    return {"_app_name": app_name, "notes": "FAILED_ALL_RETRIES", "error": str(last_err)}

def get_col(row, *possible_keys):
    """Helper to safely fetch column values regardless of CSV header naming."""
    for key in possible_keys:
        if key in row and row[key]:
            return row[key].strip()
    return ""

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Missing {INPUT_CSV}. Expected columns: app_name, hint, category")
        sys.exit(1)

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    done = already_done(OUTPUT_JSONL)
    
    # Safely match app name regardless of CSV column header variations
    remaining = [
        r for r in rows 
        if get_col(r, "app_name", "name", "App Name", "app") not in done
    ]

    print(f"Total apps: {len(rows)} | Already done: {len(done)} | Remaining: {len(remaining)}\n")

    with open(OUTPUT_JSONL, "a", encoding="utf-8") as out:
        for i, row in enumerate(remaining, 1):
            app_name = get_col(row, "app_name", "name", "App Name", "app")
            hint = get_col(row, "hint", "domain", "Domain", "url")
            category = get_col(row, "category", "Category")

            if not app_name:
                continue

            print(f"[{i}/{len(remaining)}] Researching {app_name}...")
            result = run_with_retries(app_name, hint, category)
            result["_app_name"] = app_name

            # Output the payload so you can watch results stream live to the terminal
            print(json.dumps(result, indent=2) + "\n")

            out.write(json.dumps(result) + "\n")
            out.flush()  # Write immediately so progress is saved

            if i < len(remaining):
                time.sleep(DELAY_SECONDS)

    print(f"Done. Results saved to {OUTPUT_JSONL}")

if __name__ == "__main__":
    main()