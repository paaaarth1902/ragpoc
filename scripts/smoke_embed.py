import asyncio
import os
from openai import AsyncOpenAI
from app.embeddings.openai import OpenAIEmbedder
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])
    embedder = OpenAIEmbedder(client=client)

    sample_texts = [
        "Paris is a capital of France",
        "How do I restore paused SLA clock",
        "The quick brown fox jumps over the lazy dog"
    ]

    vectors = await embedder.embed(sample_texts)

    print(f"Receieved: {len(vectors)} vectors. Each with dmimension: {len(vectors[0])}")
    print(f"first 5 dims of vector 0: {vectors[0][:5]}")
    print(f"first 5 dims of vector 1: {vectors[1][:5]}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())