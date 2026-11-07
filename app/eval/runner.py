from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_embedder

from app.eval.cases import EVAL_CASES
from app.eval.metrics import hit_at_k, mrr

from app.query.embed import embed_query
from app.query.hybrid_retriever import HybridRetriever
from app.query.keyword_retriever import KeywordRetriever
from app.query.retriever import PgVectorRetriever

TOP_K = 5

async def run_eval(session: AsyncSession) -> None:
    embedder = get_embedder()
    vector = PgVectorRetriever(session)
    hybrid = HybridRetriever(
        vector_retriever=vector,
        keyword_retriever=KeywordRetriever(session),
    )

    v_hits = h_hits = 0
    v_mrr = h_mrr = 0.0
    scored = 0

    print(f"\n{'Query':<44}{'Vector':<9}{'Hybrid':<9}")
    print("-" * 62)

    for case in EVAL_CASES:
        emb = await embed_query(embedder, case.question)
        v_res = await vector.retrieve(emb, TOP_K)
        h_res = await hybrid.retrieve_hybrid(case.question, emb, k=TOP_K)

        if not case.should_answer:
            print(f"{case.question[:42]:<44}{'n/a':<9}{'n/a':<9}")
            continue

        scored += 1
        v_ok = hit_at_k(v_res, case.expected_chunk_ids, TOP_K)
        h_ok = hit_at_k(h_res, case.expected_chunk_ids, TOP_K)
        v_hits += v_ok
        h_hits += h_ok
        v_mrr += mrr(v_res, case.expected_chunk_ids)
        h_mrr += mrr(h_res, case.expected_chunk_ids)

        mark = "  🎯" if (h_ok and not v_ok) else ""   # hybrid-only win
        print(
            f"{case.question[:42]:<44}"
            f"{'✅' if v_ok else '❌':<9}"
            f"{'✅' if h_ok else '❌':<9}{mark}"
        )

    print("-" * 62)
    print(f"{'HIT RATE @%d' % TOP_K:<44}{v_hits/scored:<9.0%}{h_hits/scored:<9.0%}")
    print(f"{'MRR':<44}{v_mrr/scored:<9.3f}{h_mrr/scored:<9.3f}")
    print()