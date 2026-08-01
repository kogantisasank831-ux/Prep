from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractionCommand:
    filename: str
    declared_media_type: str
    upload_media_type: str
    correlation_id: str
    content: bytes


@dataclass(frozen=True, slots=True)
class ExtractedDocument:
    correlation_id: str
    media_type: str
    text: str
    character_count: int
    line_count: int


def normalize_newlines(text: str) -> str:
    """Normalize newline representation without trimming other whitespace."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def count_logical_lines(text: str) -> int:
    """Count logical lines for a non-empty document."""
    lines = text.splitlines()
    return len(lines) if lines else 1
