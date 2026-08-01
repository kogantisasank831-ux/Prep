from typing import Protocol


class TextReader(Protocol):
    """Narrow interface required by the extraction service."""

    def decode(self, content: bytes) -> str: ...
