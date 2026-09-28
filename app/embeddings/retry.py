import asyncio
import random

from openai import (APIConnectionError,APITimeoutError,InternalServerError,RateLimitError)

from app.embeddings.types import Embedder

DEFAULT_RETRYABLE: tuple[type[Exception], ...] = (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError)

class RetryingEmbedder:
    dim: int

    def __init__(self, inner: Embedder, *, max_attempts: int = 5, base_delay: float = 1.0, max_delay: float = 60.0, retryable: tuple[type[Exception], ...] = DEFAULT_RETRYABLE) -> None:
        self._inner = inner
        self.dim = inner.dim
        self._max_attempts = max_attempts
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._retryable = retryable

    async def embed(self, texts: list[str]) -> list[list[float]]:
        for attempt in range(1, self._max_attempts + 1):
            try:
                return await self._inner.embed(texts)
            except self._retryable as exc:
                if attempt == self._max_attempts:
                    raise
                delay = min(self._base_delay * 2 ** (attempt - 1), self._max_delay)
                delay *= 0.75 + random.random() * 0.5  # ±25% jitter
                await asyncio.sleep(delay)
        raise RuntimeError("unreachable")