from __future__ import annotations

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_embedder
from app.embeddings.fake import FakeEmbedder
from app.main import app

_SAMPLE = Path("corpus/samples/doc-001-example-runbook.md")


@pytest.fixture
def client():
    # swap the real OpenAI embedder for the offline fake
    app.dependency_overrides[get_embedder] = lambda: FakeEmbedder(dim=1536)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_post_returns_202_and_job_id(client):
    with _SAMPLE.open("rb") as f:
        resp = client.post("/api/v1/documents", files={"file": ("doc.md", f, "text/markdown")})
    assert resp.status_code == 202
    body = resp.json()
    assert "job_id" in body
    assert body["status"] == "queued"


def test_job_reaches_succeeded(client):
    with _SAMPLE.open("rb") as f:
        job_id = client.post(
            "/api/v1/documents", files={"file": ("doc.md", f, "text/markdown")}
        ).json()["job_id"]

    # TestClient ran the background task synchronously — it's already done
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    body = status_resp.json()
    assert body["status"] == "succeeded"
    assert body["document_id"] is not None


def test_unknown_job_returns_404(client):
    resp = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_malformed_job_id_returns_422(client):
    resp = client.get("/api/v1/jobs/not-a-uuid")
    assert resp.status_code == 422


def test_same_file_twice_is_idempotent(client):
    def post():
        with _SAMPLE.open("rb") as f:
            jid = client.post(
                "/api/v1/documents", files={"file": ("doc.md", f, "text/markdown")}
            ).json()["job_id"]
        return client.get(f"/api/v1/jobs/{jid}").json()["document_id"]

    first_doc_id = post()
    second_doc_id = post()
    assert first_doc_id == second_doc_id   # same content → same document