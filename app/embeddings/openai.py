from openai import AsyncOpenAI

class OpenAIEmbedder:
    dim: int

    def __init__(self, client: AsyncOpenAI, model: str = "text-embedding-3-small", dim: int=1536, batch_size: int=100) -> None:
        self._client = client
        self._model = model
        self.dim = dim
        self.batch_size = batch_size

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts: return []
        vectors: list[list[float]] = []
        for s in range(0, len(texts), self.batch_size):
            batch = texts[s: s + self.batch_size]
            response = await self._client.embeddings.create(model=self._model, input=batch)
            vectors.extend(i.embedding for i in response.data)
        
        return vectors
