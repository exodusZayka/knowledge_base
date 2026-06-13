from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.chunking import Chunker, FixedSizedChunker


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path('./env/.env'),
        frozen=True,
    )


class GoogleSearchConfig(BaseConfig):
    GOOGLE_SEARCH_BASE_URL: str = Field(
        default='https://serpapi.com',
        description='Google search API for crawling',
    )
    GOOGLE_SEARCH_API_KEY: str = Field(description='API key for Google search')
    INITIAL_NUMBER_OF_LINKS_TO_SEARCH: int = Field(default=10, description='Number of links to start crawling')
    MAX_PROCESSED_LINK_NUMBER: int = Field(
        default=100,
        description='Max number of links to process',
    )


class TokenizerConfig(BaseConfig):
    encoding_model: str = 'o200k_base'


class ChunkerConfig(BaseConfig):
    chunker: type[Chunker] = FixedSizedChunker
    chunk_size: int = 50
    overlap: int = 5


class EmbedderConfig(BaseConfig):
    _embedding_model_dimension_mapper: dict[str, int] = {
        'qwen3-embedding:0.6b': 1024,
    }

    embedding_model: str = 'qwen3-embedding:0.6b'
    vector_size: int = _embedding_model_dimension_mapper.get(embedding_model)


class Config(
    GoogleSearchConfig,
    TokenizerConfig,
    ChunkerConfig,
    EmbedderConfig,
):
    pass


config = Config()
