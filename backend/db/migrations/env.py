"""
Alembic Migration Environment

Configures Alembic for database migrations with SQLModel support.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add backend directory to path for imports (env.py is in backend/db/migrations/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlmodel import SQLModel
from sqlalchemy import MetaData
from utils.config import settings

# Import all models to ensure they're registered with metadata
from models.session import Session
from models.chat import ChatHistory, Citation
from models.book import Chapter, Paragraph

# Hackathon Bonus Features models
from models.user import User, Base as UserBase
from models.personalized_content import PersonalizedContent
from models.translation import Translation

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set SQLAlchemy URL from environment variable
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Combine metadata from SQLModel and User's Base
# This ensures Alembic can see all tables
target_metadata = MetaData()
for table in SQLModel.metadata.tables.values():
    table.to_metadata(target_metadata)
for table in UserBase.metadata.tables.values():
    table.to_metadata(target_metadata)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
