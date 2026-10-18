from __future__ import annotations
from typing import Protocol
from openai import AsyncOpenAI
from app.query.context import GroundedContext

class AnswerGenerator(Protocol):
    async def generate(self, question: str, context: GroundedContext) -> str:
        pass

class FakeGenerator:
    async def generate(self, question: str, context: GroundedContext) -> str:
        return f"ANSWER to '{question}' using {len(context.citations)} sources"

SYSTEM_PROMPT = (
    "You are a grounded assistant. Answer the user's question using ONLY the "
    "numbered context below. Cite sources inline with their number, e.g. [1]. "
    "If the context does not contain the answer, say you don't know. "
    "Do not use outside knowledge."
)

class OpenAIGenerator:
    """Real LLM answer generator — grounded + citing."""

    def __init__(self, client: AsyncOpenAI, model: str = "gpt-4o-mini") -> None:
        self._client = client
        self._model = model

    async def generate(self, question: str, context: GroundedContext) -> str:
        user_msg = f"Context:\n{context.prompt_block}\n\nQuestion: {question}"
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0,
        )
        return resp.choices[0].message.content or ""