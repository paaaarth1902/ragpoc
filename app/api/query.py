from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_embedder, get_generator, get_reranker
from app.api.schemas import CitationOut, QueryRequest, QueryResponse
from app.db.session import get_db_session
from app.embeddings.types import Embedder
from app.query.generator import AnswerGenerator
from app.query.hybrid_retriever import HybridRetriever
from app.query.keyword_retriever import KeywordRetriever
from app.query.pipeline import QueryPipeline
from app.query.rerank import Reranker
from app.query.retriever import PgVectorRetriever

router = APIRouter(prefix="/api/v1", tags=["query"])

@router.post("/query", response_model=QueryResponse)
async def query_endpoint(body: QueryRequest, session: AsyncSession = Depends(get_db_session), embedder: Embedder = Depends(get_embedder), reranker: Reranker = Depends(get_reranker), generator: AnswerGenerator = Depends(get_generator)) -> QueryResponse:

    retriever = HybridRetriever(
        vector_retriever=PgVectorRetriever(session),
        keyword_retriever=KeywordRetriever(session),
    )
    pipeline = QueryPipeline(embedder, retriever, reranker, generator)
    result = await pipeline.run(body.question, k=body.k)

    return QueryResponse(
        answer=result.answer,
        citations=[
            CitationOut(label=c.label, chunk_id=c.chunk_id, document_id=c.document_id)
            for c in result.citations
        ],
    )