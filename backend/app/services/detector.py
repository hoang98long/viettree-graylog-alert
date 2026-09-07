import re
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionResult:
    detected: bool
    event_type: str = "Configuration Change"
    severity: str = "WARNING"
    reason: str = ""
    matched_pattern: str | None = None


class ConfigChangeDetector:
    """Editable vendor-neutral patterns; tune these with real firewall logs."""
    patterns = (
        r"\bconfigured\b", r"\bconfiguration(?:\s+change)?\b", r"\bconfiguration\s+(?:modified|changed)\b", r"\bconfig\s+change\b",
        r"\bexecuted\s+(?:the\s+)?command\b", r"\bcommand\s+execut(?:ed|ion)\b",
        r"\bmodified\b", r"\bconfig(?:uration)?\s+(?:updated|modified)\b",
        r"\badministrative\s+action\b", r"\bconfigure\s+terminal\b", r"\bwrite\s+(?:memory|running-config)\b",
        r"\bcopy\s+running-config\s+startup-config\b", r"\b(?:created|updated|removed)\s+firewall\s+rule\b",
    )
    critical_patterns = (r"\berase\b", r"\bwrite\s+erase\b", r"\bdisable\b.*\bfirewall\b")

    def detect(self, message: str) -> DetectionResult:
        text = message or ""
        matched = next((pattern for pattern in self.patterns if re.search(pattern, text, re.IGNORECASE)), None)
        if not matched:
            return DetectionResult(False)
        severity = "CRITICAL" if any(re.search(p, text, re.IGNORECASE) for p in self.critical_patterns) else "WARNING"
        return DetectionResult(True, severity=severity, reason="Matched configuration change pattern", matched_pattern=matched)
