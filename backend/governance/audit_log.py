from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AuditEvent:
    event_id: str
    timestamp: str
    agent_id: str
    event_type: str
    details: dict[str, Any]
    append_only: bool = True


class AuditLog:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._events: list[AuditEvent] = []

    def log(self, agent_id: str, event_type: str, details: dict[str, Any]) -> AuditEvent | None:
        if not self.enabled:
            return None
        event = AuditEvent(
            event_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=agent_id,
            event_type=event_type,
            details=details,
        )
        self._events.append(event)
        return event

    def export(self) -> list[dict[str, Any]]:
        return [asdict(event) for event in self._events]

    def clear(self) -> None:
        self._events.clear()