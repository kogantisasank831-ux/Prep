from typing import ClassVar

from document_service.errors import ReaderDecodingError


class Utf8TextReader:
    """Decode complete UTF-8 document content strictly."""

    encoding: ClassVar[str] = "utf-8"

    def decode(self, content: bytes) -> str:
        try:
            return content.decode(self.encoding, errors="strict")
        except UnicodeDecodeError as exc:
            raise ReaderDecodingError("document resource is not valid UTF-8") from exc
