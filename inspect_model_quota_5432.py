import psycopg2

conn = psycopg2.connect(dbname='Model Quota', user='postgres', password='Admin', host='localhost', port=5432)
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_schema, table_name")
tables = cur.fetchall()
print('tables:', tables)
cur.close()
conn.close()