from __future__ import annotations

import re

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*[^\s]+"),
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
]

def redact_secrets(text: str) -> str:
    result=text
    for pattern in SECRET_PATTERNS:
        result=pattern.sub("[REDACTED_SECRET]", result)
    return result

def prompt_injection_signal(text: str) -> bool:
    signals=("ignore previous instructions", "reveal system prompt", "disable safety", "exfiltrate secrets")
    lowered=text.casefold()
    return any(signal in lowered for signal in signals)
