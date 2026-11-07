from __future__ import annotations

import asyncio
from app.db.session import SessionLocal
from app.eval.runner import run_eval

async def main() -> None:
    async with SessionLocal() as session:
        await run_eval(session)\

if __name__ == "__main__":
    asyncio.run(main())