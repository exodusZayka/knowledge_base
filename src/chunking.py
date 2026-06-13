from abc import ABC, abstractmethod


class Chunker(ABC):
    @classmethod
    @abstractmethod
    def chunk(cls, text: list[str], chunk_size: int, overlap: int = 0) -> list[list[str]]:
        pass


class FixedSizedChunker(Chunker):
    @classmethod
    def chunk(
        cls,
        text: list[str],
        chunk_size: int,
        overlap: int = 0,
    ) -> list[list[str]]:
        if overlap >= chunk_size:
            raise ValueError('Overlap must be less than chunk_size')

        chunked_text: list[list[str]] = []
        i = 0
        right_boarder = 0
        while right_boarder < len(text):
            right_boarder = min(i + chunk_size, len(text))
            chunked_text.append(text[i:right_boarder])
            i = right_boarder - overlap
        return chunked_text
