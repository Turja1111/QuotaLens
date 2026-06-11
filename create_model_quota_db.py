import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(dbname='postgres', user='quotalens', password='password', host='localhost', port=5433)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ('Model Quota',))
if cur.fetchone() is None:
    cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier('Model Quota')))
    print('created Model Quota database')
else:
    print('Model Quota database already exists')
cur.close()
conn.close()
