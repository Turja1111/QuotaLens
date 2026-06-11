#!/usr/bin/env bash
set -e

# Wait for Postgres to become available using psycopg2
PY_CMD="""import time, sys, os
import urllib.parse as up
from time import sleep
url=os.environ.get('DATABASE_URL_SYNC') or os.environ.get('DATABASE_URL')
if url and '+asyncpg' in url:
    url=url.replace('+asyncpg','')
if not url:
    print('No database URL provided')
    sys.exit(1)
parsed=up.urlparse(url)
for i in range(60):
    try:
        import psycopg2
        conn=psycopg2.connect(dbname=parsed.path.lstrip('/'), user=parsed.username, password=parsed.password, host=parsed.hostname, port=parsed.port)
        conn.close()
        print('Postgres available')
        break
    except Exception as e:
        print('Waiting for Postgres...', e)
        sleep(1)
else:
    print('Postgres did not become available in time')
    sys.exit(1)
"""
python - <<PY
$PY_CMD
PY

# Run alembic migrations (config paths are relative to repo root)
echo "Running alembic migrations"
cd /app
if ! alembic -c /app/alembic.ini upgrade head 2>/tmp/alembic.err; then
  if grep -qiE "DuplicateTable|already exists" /tmp/alembic.err; then
    echo "Schema already present — stamping Alembic head"
    alembic -c /app/alembic.ini stamp head
  else
    cat /tmp/alembic.err
    exit 1
  fi
fi
cd /app/backend

# Start uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 8000
