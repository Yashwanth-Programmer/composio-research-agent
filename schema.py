from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AppResearch:
    app: str
    category: str
    one_liner: str = ""
    auth_methods: list = field(default_factory=list)   # ["OAuth2","API key",...]
    self_serve: str = ""      # "self-serve" | "gated" | "unclear"
    gate_reason: str = ""     # paid plan / admin approval / contact-sales
    api_surface: str = ""     # REST / GraphQL / both / none
    api_breadth: str = ""     # narrow / broad
    mcp_exists: bool = False
    buildability: str = ""    # "yes" | "no" | "partial"
    blocker: str = ""
    evidence_url: str = ""
    confidence: float = 0.0
    notes: str = ""