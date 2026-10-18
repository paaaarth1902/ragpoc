from openai import AsyncOpenAI
from app.config import get_settings
from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder
from app.query.generator import OpenAIGenerator, AnswerGenerator

def get_embedder() -> Embedder:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return RetryingEmbedder(inner=OpenAIEmbedder(client=client))

def get_generator() -> AnswerGenerator:
    settings = get_settings()
    client = OpenAIGenerator(AsyncOpenAI(api_key=settings.openai_api_key))
    return client
# single prod source of real embedder