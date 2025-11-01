import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 1

    _failures: Optional[Dict[str, int]] = field(default=None)
    _open_until: Optional[Dict[str, float]] = field(default=None)
    _half_open_calls: Optional[Dict[str, int]] = field(default=None)

    def __post_init__(self):
        self._failures = {}
        self._open_until = {}
        self._half_open_calls = {}

    def state(self, key: str) -> str:
        now = time.time()

        if key in self._open_until:
            if now >= self._open_until[key]:
                return "half-open"
            return "open"
        return "closed"

    def record_success(self, key: str):
        self._failures[key] = 0
        self._open_until.pop(key, None)
        self._half_open_calls.pop(key, None)

    def record_failure(self, key: str):
        self._failures[key] = self._failures.get(key, 0) + 1

        if self._failures[key] >= self.failure_threshold:
            self._open_until[key] = time.time() + self.recovery_timeout

    def allow_call(self, key: str) -> bool:
        state = self.state(key)

        if state == "closed":
            return True

        if state == "open":
            return False

        # half-open
        calls = self._half_open_calls.get(key, 0)
        if calls < self.half_open_max_calls:
            self._half_open_calls[key] = calls + 1
            return True

        return False
