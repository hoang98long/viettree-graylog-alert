import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionResult:
    detected: bool
    event_type: str = "Configuration Change"
    severity: str = "WARNING"


class ConfigChangeDetector:
    """Editable ASA-oriented patterns; tune these with real Graylog samples."""
    patterns = (
        r"\bconfigured\b", r"\bconfiguration(?:\s+change)?\b", r"\bconfig\s+change\b",
        r"\bexecuted\s+(?:the\s+)?command\b", r"\bcommand\s+execut(?:ed|ion)\b",
        r"\bmodified\b", r"\bconfig(?:uration)?\s+(?:updated|modified)\b",
        r"\badministrative\s+action\b",
    )
    critical_patterns = (r"\berase\b", r"\bwrite\s+erase\b", r"\bdisable\b.*\bfirewall\b")

    def detect(self, message: str) -> DetectionResult:
        text = message or ""
        if not any(re.search(pattern, text, re.IGNORECASE) for pattern in self.patterns):
            return DetectionResult(False)
        severity = "CRITICAL" if any(re.search(p, text, re.IGNORECASE) for p in self.critical_patterns) else "WARNING"
        return DetectionResult(True, severity=severity)
