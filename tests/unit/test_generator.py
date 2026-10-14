from __future__ import annotations

import pytest
from uuid import UUID

from app.query.context import GroundedContext, Citation
from app.query.generator import FakeGenerator

@pytest.mark.asyncio
async def test_fake_generator_echoes_inputs():
    ctx = GroundedContext( 
        prompt_block="[1] cats\n\n[2] dogs",
        citations=[
            Citation(label=1, chunk_id=10, document_id=UUID(int=1)),
            Citation(label=2, chunk_id=20, document_id=UUID(int=1)),
        ],
    )
    gen = FakeGenerator()
    answer = await gen.generate("what pets are mentioned?", ctx)

    assert "what pets are mentioned?" in answer  # received the question
    assert "2" in answer                          # saw 2 sources