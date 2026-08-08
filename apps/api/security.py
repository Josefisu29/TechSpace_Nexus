from __future__ import annotations

import re

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

def redact_secrets(text: str) -> str:
    out = text
    for pattern in SECRET_PATTERNS: out = pattern.sub("[REDACTED_SECRET]", out)
    return out

def looks_like_prompt_injection(text: str) -> bool:
    p = text.casefold()
    markers = ("ignore previous instructions", "reveal system prompt", "developer message", "bypass safety")
    return any(marker in p for marker in markers)
