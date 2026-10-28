from openai import AsyncOpenAI
from app.config import get_settings
from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder
from app.query.generator import OpenAIGenerator, AnswerGenerator
from functools import lru_cache
from app.query.rerank_cross_encoder import CrossEncoderReranker
from app.query.rerank import Reranker

def get_embedder() -> Embedder:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return RetryingEmbedder(inner=OpenAIEmbedder(client=client))

def get_generator() -> AnswerGenerator:
    settings = get_settings()
    client = OpenAIGenerator(AsyncOpenAI(api_key=settings.openai_api_key))
    return client

@lru_cache(maxsize=1)
def _reranker_singleton() -> CrossEncoderReranker:
    return CrossEncoderReranker()

def get_reranker() -> Reranker:
    return _reranker_singleton()