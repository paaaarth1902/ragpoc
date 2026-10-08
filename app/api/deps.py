from openai import AsyncOpenAI
from app.config import get_settings
from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder

def get_embedder() -> Embedder:
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return RetryingEmbedder(inner=OpenAIEmbedder(client=client))

# single prod source of real embedder