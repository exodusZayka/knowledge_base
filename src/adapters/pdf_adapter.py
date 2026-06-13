from pypdf import PdfReader


class PDFAdapter:
    def __enter__(self, file_path: str) -> PdfReader:
        return PdfReader('knowledge_base/clean-code.pdf')