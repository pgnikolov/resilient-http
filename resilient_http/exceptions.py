class ResilientHTTPError(Exception):
    """Base exception."""


class CircuitOpenError(ResilientHTTPError):
    def __init__(self, key: str):
        super().__init__(f"Circuit open for {key}")
        self.key = key
