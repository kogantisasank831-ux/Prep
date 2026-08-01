import pytest

from document_service.errors import ReaderDecodingError
from document_service.readers import Utf8TextReader


def test_reader_decodes_utf8_text() -> None:
    result = Utf8TextReader().decode("भारत\nAI".encode())

    assert result == "भारत\nAI"


def test_reader_rejects_invalid_utf8() -> None:
    with pytest.raises(ReaderDecodingError) as captured:
        Utf8TextReader().decode(b"\xff\xfe\xfa")

    assert isinstance(captured.value.__cause__, UnicodeDecodeError)
