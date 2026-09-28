import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.ingestion.pipeline import ingest_document
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    path = Path("corpus/samples/doc-001-example-runbook.md")
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    embedder = RetryingEmbedder(inner=OpenAIEmbedder(client=client))

    embedded = await ingest_document(path, embedder=embedder)

    print(f"{path.name}: {len(embedded)} chunks embedded, dim={len(embedded[0].vector)}")
    for c in embedded[:3]:
        head = " > ".join(c.heading_path)
        print(f"  chunk {c.chunk_index}: {c.token_count} tokens, [{head}]")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())