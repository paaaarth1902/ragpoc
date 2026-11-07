from functools import lru_cache

from fastapi import Depends
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db_session

from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder
from app.query.retriever import PgVectorRetriever

from app.query.generator import AnswerGenerator, OpenAIGenerator
from app.query.hybrid_retriever import HybridRetriever
from app.query.keyword_retriever import KeywordRetriever

from app.query.rerank import Reranker
from app.query.rerank_cross_encoder import CrossEncoderReranker



def get_embedder() -> Embedder:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return RetryingEmbedder(inner=OpenAIEmbedder(client=client))


def get_generator() -> AnswerGenerator:
    settings = get_settings()
    return OpenAIGenerator(AsyncOpenAI(api_key=settings.openai_api_key))


@lru_cache(maxsize=1)
def _reranker_singleton() -> CrossEncoderReranker:
    return CrossEncoderReranker()


def get_reranker() -> Reranker:
    return _reranker_singleton()


def get_retriever(session: AsyncSession = Depends(get_db_session)) -> HybridRetriever:
    return HybridRetriever(
        vector_retriever=PgVectorRetriever(session),
        keyword_retriever=KeywordRetriever(session),
    )