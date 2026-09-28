import pytest

from app.embeddings.fake import FakeEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.embeddings.types import Embedder


class _TransientError(Exception):
    pass


class _FlakyEmbedder:
    """Wraps an Embedder, raises _TransientError the first N times."""
    dim: int

    def __init__(self, inner: Embedder, fail_count: int) -> None:
        self._inner = inner
        self.dim = inner.dim
        self._remaining = fail_count
        self.call_count = 0

    async def embed(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        if self._remaining > 0:
            self._remaining -= 1
            raise _TransientError("simulated")
        return await self._inner.embed(texts)


@pytest.mark.asyncio
async def test_retries_transient_and_succeeds():
    flaky = _FlakyEmbedder(FakeEmbedder(dim=32), fail_count=2)
    embedder = RetryingEmbedder(
        inner=flaky,
        max_attempts=5,
        base_delay=0.001,      # keep tests fast
        retryable=(_TransientError,),
    )
    vectors = await embedder.embed(["hello"])
    assert len(vectors) == 1
    assert len(vectors[0]) == 32
    assert flaky.call_count == 3   # 2 failures + 1 success


@pytest.mark.asyncio
async def test_gives_up_after_max_attempts():
    flaky = _FlakyEmbedder(FakeEmbedder(dim=32), fail_count=99)
    embedder = RetryingEmbedder(
        inner=flaky,
        max_attempts=3,
        base_delay=0.001,
        retryable=(_TransientError,),
    )
    with pytest.raises(_TransientError):
        await embedder.embed(["hello"])
    assert flaky.call_count == 3   # exactly max_attempts, then re-raise


@pytest.mark.asyncio
async def test_does_not_retry_non_retryable():
    class _Boom(Exception):
        pass

    class _AlwaysBoom:
        dim: int = 32
        call_count = 0
        async def embed(self, texts):
            self.call_count += 1
            raise _Boom("won't fix itself")

    boom = _AlwaysBoom()
    embedder = RetryingEmbedder(
        inner=boom,
        max_attempts=5,
        base_delay=0.001,
        retryable=(_TransientError,),   # deliberately doesn't include _Boom
    )
    with pytest.raises(_Boom):
        await embedder.embed(["hello"])
    assert boom.call_count == 1   # never retried