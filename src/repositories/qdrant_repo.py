from typing import Any
from uuid import uuid4

from loguru import logger
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.conversions.common_types import PointStruct, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance

from config import config
from .base_repository import BaseVectorDBRepo
from .exceptions import CannotSaveVectorException


class _QdrantClient(AsyncQdrantClient):
    def __init__(self) -> None:
        super().__init__(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
        )

    def __call__(self, collection_name: str, *args, **kwargs) -> '_QdrantClient':
        self._collection_name = collection_name
        return self

    async def __aenter__(self) -> AsyncQdrantClient:
        await self._create_collection_if_not_exists(self._collection_name)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            logger.error(
                'Cannot save vector to db',
                exc_type=exc_type,
                exc_info=exc_val,
            )
        await self.close()
        raise CannotSaveVectorException(exc_val) from exc_type

    async def _create_collection_if_not_exists(self, collection_name: str) -> None:
        try:
            await self.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config.vector_size,
                    distance=Distance.COSINE,
                )
            )
        except UnexpectedResponse:
            logger.info(f'Collection {collection_name} already exists')


class QdrantRepo(BaseVectorDBRepo):
    def __init__(self) -> None:
        self._client = _QdrantClient()

    async def save_chunked_data(
        self,
        collection_name: str,
        data: list[list[list[float]]],
        metadata: dict[str, Any] | None = None,
    ):
        metadata = metadata or {}

        async with self._client(collection_name) as qdrant_client:
            await qdrant_client.upsert(
                collection_name=collection_name,
                points=[
                    PointStruct(
                        id=uuid4(),
                        vector=vector[0],
                        payload={'text': vector, **metadata}
                    )
                    for vector in data
                ]
            )
        logger.info('Data was saved to QDrant successfully')
