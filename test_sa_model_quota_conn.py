from sqlalchemy import create_engine, text

urls = [
    'postgresql://quotalens:password@localhost:5433/Model%20Quota',
    'postgresql://quotalens:password@localhost:5433/?dbname=Model%20Quota',
    'postgresql://quotalens:password@localhost:5433/?dbname=Model+Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?dbname=Model%20Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?dbname=Model+Quota',
]

for url in urls:
    print('URL:', url)
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print('  result:', result.scalar())
    except Exception as e:
        print('  error:', type(e).__name__, e)
    print()