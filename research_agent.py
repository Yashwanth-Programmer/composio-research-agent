import json, os
from composio import Composio
from composio_gemini import GeminiProvider
from google import genai
from google.genai import types

composio = Composio(provider=GeminiProvider())
client = genai.Client()  # picks up GOOGLE_API_KEY automatically

USER_ID = "research_agent_v1"
MODEL = "gemini-3.6-flash"
session = composio.create(user_id=USER_ID, toolkits=["composio_search"])
tools = session.tools()

SYSTEM = """You are a research agent investigating a software app for API/agent buildability.
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
    prompt = f"{SYSTEM}\n\nApp: {app_name}\nHint: {hint}\nCategory: {category}\nResearch it now."

    config = types.GenerateContentConfig(tools=tools)
    chat = client.chats.create(model=MODEL, config=config)
    response = chat.send_message(prompt)  # Automatic Function Calling handles the tool loop

    text = response.text
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip().strip("`").replace("json\n", "", 1)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {"app": app_name, "notes": "PARSE_FAILED", "raw": text}