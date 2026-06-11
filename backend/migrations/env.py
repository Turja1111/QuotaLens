"""Alembic async migration environment for QuotaLens."""

import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool, engine_from_config
from alembic import context

# Add backend to path so models can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow overriding the SQLAlchemy URL via environment variables when running inside containers.
# Prefer DATABASE_URL_SYNC (sync driver) or fall back to DATABASE_URL (strip +asyncpg if present).
env_db = os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL")
if env_db:
    if "+asyncpg" in env_db:
        env_db = env_db.replace("+asyncpg", "")
    # Preserve literal percent-encoding in configparser values.
    config.set_main_option("sqlalchemy.url", env_db.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    if env_db:
        url = env_db

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    if env_db:
        connectable = engine_from_config(
            {"sqlalchemy.url": env_db},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
