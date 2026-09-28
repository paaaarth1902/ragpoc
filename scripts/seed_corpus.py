import asyncio
import os
from pathlib import Path
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.embeddings.openai import OpenAIEmbedder
from app.embeddings.retry import RetryingEmbedder
from app.ingestion.seed import seed_document
from dotenv import load_dotenv

load_dotenv()

CORPUS_DIR = Path("corpus/samples")

async def main() -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"])
    maker = async_sessionmaker(engine, expire_on_commit=False)

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    embedder = RetryingEmbedder(inner=OpenAIEmbedder(client=client))

    ingested = skipped = 0
    for path in sorted(CORPUS_DIR.glob("*.md")):
        async with maker() as session:
            async with session.begin():
                doc_id, was_new = await seed_document(session, path, embedder)
        if was_new:
            ingested += 1
            print(f"  ingested  {path.name} -> {doc_id}")
        else:
            skipped += 1
            print(f"  skipped   {path.name} (already ingested)")

    print(f"\n{ingested} ingested, {skipped} skipped.")

    await client.close()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())