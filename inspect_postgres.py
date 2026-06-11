import psycopg2
from psycopg2 import sql

ports = [5432, 5433]
dbs = ['postgres', 'model_quota', 'Model Quota']

for port in ports:
    print(f'PORT {port}')
    for db in dbs:
        try:
            conn = psycopg2.connect(dbname=db, user='quotalens', password='password', host='localhost', port=port)
            cur = conn.cursor()
            cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_schema, table_name")
            tables = cur.fetchall()
            print(f'  DB {db!r}: connected, tables={len(tables)}')
            for schema, name in tables:
                print(f'    {schema}.{name}')
            cur.close()
            conn.close()
        except Exception as exc:
            print(f'  DB {db!r}: ERROR {exc.__class__.__name__}: {exc}')
    print()