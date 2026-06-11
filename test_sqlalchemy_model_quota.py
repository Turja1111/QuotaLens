from sqlalchemy import create_engine

urls = [
    'postgresql://quotalens:password@localhost:5433/Model%20Quota',
    'postgresql://quotalens:password@localhost:5433/?dbname=Model%20Quota',
    'postgresql://quotalens:password@localhost:5433/?dbname=Model+Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/Model%20Quota',
    'postgresql+asyncpg://quotalens:password@localhost:5433/?dbname=Model%20Quota',
]

for url in urls:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute('SELECT 1')
            print(url, 'OK', result.scalar())
    except Exception as e:
        print(url, 'ERROR', type(e).__name__, e)
