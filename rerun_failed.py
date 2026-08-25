import concurrent.futures
import csv
import json
import os
import re
import sys
import time
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types

INPUT_CSV = "apps.csv"
OUTPUT_JSONL = "results.jsonl"
BACKUP_JSONL = "results_backup_before_retry.jsonl"
DELAY_SECONDS = 5
MAX_RETRIES = 4
CALL_TIMEOUT_SECONDS = 180
MODEL = "gemini-3.5-flash-lite"
USER_ID = "research_agent_v1"

FAILED_NOTES = {"PARSE_FAILED", "FAILED_ALL_RETRIES", "MAX_TURNS_EXCEEDED"}

SYSTEM_PROMPT = """You are a research agent investigating a software app for API/agent buildability.
Use web search tools available to you to find real, current information.
Given an app name and hint URL, find:
- one_liner: what app does, one line
- auth_methods: list, e.g. [\"OAuth2\"], [\"API key\"], etc
- self_serve: \"self-serve\" or \"gated\"
- gate_reason: if gated, why (paid plan / admin approval / contact-sales / none)
- api_surface: \"REST\" / \"GraphQL\" / \"both\" / \"none\"
- api_breadth: \"narrow\" / \"broad\"
- mcp_exists: true or false
- buildability: \"yes\" / \"no\" / \"partial\"
- blocker: main blocker if not buildable, else \"\"
- evidence_url: exact docs URL you found this from
- confidence: 0.0-1.0

When done, respond with ONLY a valid JSON object, no markdown fences and no prose.
Do not stop after a tool call. Finish the research and return the JSON object."""

try:
    composio_client = Composio(provider=GeminiProvider())
    gemini_client = genai.Client()
    session = composio_client.create(user_id=USER_ID, toolkits=["composio_search"])
    COMPOSIO_TOOLS = session.tools()
except Exception as e:
    print(f"Initialization failed: {e}")
    print("Check COMPOSIO_API_KEY and GEMINI_API_KEY in .env")
    sys.exit(1)


def extract_text(response):
    """Safely extract text even when response.text is empty because parts contain tool calls."""
    try:
        text = response.text
        if text:
            return text
    except Exception:
        pass

    chunks = []
    try:
        for candidate in (response.candidates or []):
            content = getattr(candidate, "content", None)
            for part in (getattr(content, "parts", None) or []):
                part_text = getattr(part, "text", None)
                if part_text:
                    chunks.append(part_text)
    except Exception:
        pass
    return "\n".join(chunks).strip()


def research_app(app_name, hint, category):
    prompt = f"{SYSTEM_PROMPT}\n\nApp: {app_name}\nHint: {hint}\nCategory: {category}\nResearch it now."
    config = types.GenerateContentConfig(tools=COMPOSIO_TOOLS)
    chat = gemini_client.chats.create(model=MODEL, config=config)
    response = chat.send_message(prompt)
    text = extract_text(response)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip().strip("`")
        if cleaned.startswith("json\n"):
            cleaned = cleaned[5:]
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            raise RuntimeError(f"Could not parse JSON response for {app_name}: {text[:300]!r}")


def extract_retry_delay(err):
    msg = str(err)
    match = re.search(r"'retryDelay':\s*'([0-9]+)s'", msg)
    return int(match.group(1)) + 2 if match else None


def call_with_timeout(app_name, hint, category):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(research_app, app_name, hint, category)
        try:
            return future.result(timeout=CALL_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            raise RuntimeError(f"Timed out after {CALL_TIMEOUT_SECONDS}s")


def run_with_retries(app_name, hint, category):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = call_with_timeout(app_name, hint, category)
            return result
        except Exception as e:
            last_err = e
            suggested = extract_retry_delay(e)
            wait = suggested if suggested else DELAY_SECONDS * attempt * 2
            print(f"   [retry {attempt}/{MAX_RETRIES}] {app_name} failed: {e}. Waiting {wait}s...")
            time.sleep(wait)
    return {"app": app_name, "notes": "FAILED_ALL_RETRIES", "error": str(last_err)}


def get_col(row, *keys):
    for key in keys:
        if key in row and row[key]:
            return row[key].strip()
    return ""


def is_good_record(row):
    required = ["one_liner", "auth_methods", "self_serve", "gate_reason",
                "api_surface", "api_breadth", "mcp_exists", "buildability",
                "blocker", "evidence_url", "confidence"]
    return all(k in row for k in required) and row.get("notes") not in FAILED_NOTES


def main():
    if not os.path.exists(INPUT_CSV):
        sys.exit(f"Missing {INPUT_CSV}")
    if not os.path.exists(OUTPUT_JSONL):
        sys.exit(f"Missing {OUTPUT_JSONL}")

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Read current results and preserve a backup before changing anything.
    records = []
    with open(OUTPUT_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                print("Skipping malformed JSON line in existing results.jsonl")

    with open(BACKUP_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    current_by_name = {}
    order = []
    for r in records:
        name = r.get("_app_name") or r.get("app")
        if not name:
            continue
        if name not in current_by_name:
            order.append(name)
        current_by_name[name] = r

    failed = [
        name for name, r in current_by_name.items()
        if not is_good_record(r)
    ]

    # Only retry failed records that are also present in the input CSV.
    input_by_name = {}
    for row in rows:
        name = get_col(row, "app_name", "name", "App Name", "app")
        if name:
            input_by_name[name] = row

    failed = [name for name in failed if name in input_by_name]

    print(f"Existing records: {len(current_by_name)}")
    print(f"Failed records to retry: {len(failed)}")
    print("Retry list:")
    for name in failed:
        print(f"  - {name}")

    for i, name in enumerate(failed, 1):
        row = input_by_name[name]
        hint = get_col(row, "hint", "domain", "Domain", "url")
        category = get_col(row, "category", "Category")
        print(f"\n[{i}/{len(failed)}] Retrying {name}...")
        result = run_with_retries(name, hint, category)
        result["_app_name"] = name
        current_by_name[name] = result
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if i < len(failed):
            time.sleep(DELAY_SECONDS)

    # Rebuild in the original app order. Add any CSV apps not previously present at the end.
    final_names = order[:]
    for row in rows:
        name = get_col(row, "app_name", "name", "App Name", "app")
        if name and name not in final_names:
            final_names.append(name)

    temp = OUTPUT_JSONL + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        for name in final_names:
            if name in current_by_name:
                f.write(json.dumps(current_by_name[name], ensure_ascii=False) + "\n")
    os.replace(temp, OUTPUT_JSONL)

    remaining_failed = [
        name for name in final_names
        if name in current_by_name and not is_good_record(current_by_name[name])
    ]

    print("\n========================================")
    print(f"Final records: {len(final_names)}")
    print(f"Remaining failed: {len(remaining_failed)}")
    if remaining_failed:
        print("Still failed:")
        for name in remaining_failed:
            print(f"  - {name}")
    else:
        print("SUCCESS: all records have the expected research fields.")
    print(f"Backup saved as: {BACKUP_JSONL}")
    print(f"Updated results: {OUTPUT_JSONL}")
    print("========================================")


if __name__ == "__main__":
    main()