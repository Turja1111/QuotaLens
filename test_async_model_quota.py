import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

urls = [
    'postgresql+asyncpg://quotalens:password@localhost:5433/?dbname=Model%20Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?dbname=Model+Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?database=Model%20Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?database=Model+Quota',
]

async def test(url):
    print('URL:', url)
    try:
        engine = create_async_engine(url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('  result:', result.scalar())
    except Exception as e:
        print('  error:', type(e).__name__, e)

async def main():
    for url in urls:
        await test(url)
        print()

asyncio.run(main())
