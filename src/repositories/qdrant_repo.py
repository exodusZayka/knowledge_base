from typing import Any
from uuid import uuid4

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.conversions.common_types import PointStruct, VectorParams
from qdrant_client.models import Distance

from config import config
from .base_repository import BaseVectorDBRepo


class _QdrantClient(AsyncQdrantClient):
    def __init__(self) -> None:
        super().__init__(location=':memory:')

    def __call__(self, collection_name: str, *args, **kwargs) -> '_QdrantClient':
        self._collection_name = collection_name
        return self

    async def __aenter__(self) -> AsyncQdrantClient:
        await self._create_collection_if_not_exists(self._collection_name)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def _create_collection_if_not_exists(self, collection_name: str) -> None:
        await self.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=config.vector_size,
                distance=Distance.COSINE,
            )
        )


class QdrantRepo(BaseVectorDBRepo):
    def __init__(self) -> None:
        self._client = _QdrantClient()

    async def save_chunked_data(
        self,
        collection_name: str,
        data: list[list[float]],
        metadata: dict[str, Any] | None = None,
    ):
        metadata = metadata or {}

        async with self._client(collection_name) as qdrant_client:
            await qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=uuid4(),
                        vector=vector,
                        payload={'text': vector, **metadata}
                    )
                    for vector in data
                ]
            )
