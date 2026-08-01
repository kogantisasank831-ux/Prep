from document_service.readers import Utf8TextReader
from document_service.service import DocumentExtractionService


def get_extraction_service() -> DocumentExtractionService:
    reader = Utf8TextReader()
    return DocumentExtractionService(reader=reader)
