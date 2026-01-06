import os
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")


def get_database_url() -> str:
    """
    Read DB URL from environment.
    This makes Alembic usable without Flask app context.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    # Alembic treats % as interpolation
    return url.replace("%", "%%")


# ---- Load SQLAlchemy metadata (optional but safe) ----
target_metadata = None
try:
    # This project defines db in app.models
    from app.models import db  # type: ignore
    target_metadata = db.metadata
except Exception as e:
    logger.warning(
        "Could not import SQLAlchemy metadata from app.models: %s", e
    )
    target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    url = get_database_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
