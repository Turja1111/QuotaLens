import psycopg2

urls = [
    "postgresql://quotalens:password@localhost:5433/Model%20Quota",
    "postgresql://quotalens:password@localhost:5433/?dbname=Model%20Quota",
    "postgresql://quotalens:password@localhost:5433/?dbname=Model+Quota",
    "postgresql+psycopg2://quotalens:password@localhost:5433/Model%20Quota",
    "postgresql+psycopg2://quotalens:password@localhost:5433/?dbname=Model%20Quota",
    "postgresql+psycopg2://quotalens:password@localhost:5433/?dbname=Model+Quota",
]

for url in urls:
    try:
        conn = psycopg2.connect(url)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        print(url, 'OK')
        cur.close()
        conn.close()
    except Exception as e:
        print(url, 'ERROR', type(e).__name__, e)
