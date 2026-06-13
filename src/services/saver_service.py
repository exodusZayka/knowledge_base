from string import punctuation
from typing import Any

import ollama
import tiktoken

from config import config
from src.repositories.base_repository import BaseVectorDBRepo
from src.repositories.qdrant_repo import QdrantRepo


class Saver:
    def __init__(self, vector_db_repo: BaseVectorDBRepo | None = None) -> None:
        self._repo = vector_db_repo or QdrantRepo()

    async def save(self, query: str, text: str, metadata: dict[str, Any] | None = None):
        chunked_text: list[str] = self._prepare_text(text)
        embedded_text = [self.__embed_chunk(chunk) for chunk in chunked_text]

        await self._repo.save_chunked_data(
            collection_name=self._normalize_query(query),
            data=embedded_text,
            metadata=metadata,
        )

    @staticmethod
    def _prepare_text(text: str) -> list[str]:
        """
        Prepare text for storing to a vector DB.
        1. Tokenize text.
        2. Chunk the tokenized text.

        :args:
            - text: str - Text to store in a vector DB.
        :returns
            list of tokens.
        """
        tokenizer = tiktoken.get_encoding(config.encoding_model)
        tokenized_text = tokenizer.decode(tokenizer.encode(text))
        chunked_text = config.chunker.chunk(
            text=tokenized_text,
            chunk_size=config.chunk_size,
            overlap=config.overlap,
        )
        return chunked_text

    @staticmethod
    def __embed_chunk(chunk: str) -> list[float]:
        response = ollama.embed(
            model=config.embedding_model,
            input=chunk,
        )
        return response.embeddings

    @staticmethod
    def _normalize_query(query: str) -> str:
        return (
            query
            .lower()
            .translate(str.maketrans(' ', ' ', punctuation))
            .replace(' ', '_')
            .strip()
        )
