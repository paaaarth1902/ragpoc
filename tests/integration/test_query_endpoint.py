from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import get_embedder, get_generator
from app.db.session import get_db_session
from app.embeddings.fake import FakeEmbedder
from app.query.generator import FakeGenerator
from app.query.pipeline import NO_CONTEXT_ANSWER


def _apply_fakes(db_session):
    app.dependency_overrides[get_embedder] = lambda: FakeEmbedder()
    app.dependency_overrides[get_generator] = lambda: FakeGenerator()
    app.dependency_overrides[get_db_session] = lambda: db_session


@pytest.mark.asyncio
async def test_query_endpoint_returns_answer(db_session):
    # empty test DB -> retrieval finds nothing -> honest refusal, no citations
    _apply_fakes(db_session)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/query",
            json={"question": "what do pets do?", "k": 5},
        )
    app.dependency_overrides.clear()

    assert resp.status_code == 200
    data = resp.json()
    assert data["citations"] == []                # no sources on empty corpus
    assert data["answer"] == NO_CONTEXT_ANSWER    # grounded refusal


@pytest.mark.asyncio
async def test_query_endpoint_rejects_empty_question(db_session):
    _apply_fakes(db_session)   # override deps so no real OpenAI client is built
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/query", json={"question": "", "k": 5})
    app.dependency_overrides.clear()

    assert resp.status_code == 422   # Pydantic min_length guard