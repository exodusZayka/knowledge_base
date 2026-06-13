from abc import ABC, abstractmethod
from typing import Any


class BaseVectorDBRepo(ABC):
    @abstractmethod
    async def save_chunked_data(
        self,
        collection_name: str,
        data: list[list[float]],
        metadata: dict[str, Any] | None = None,
    ):
        pass
