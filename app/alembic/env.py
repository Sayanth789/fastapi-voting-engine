from logging.config import fileConfig
import sys
import os

from sqlalchemy import create_engine, pool
from alembic import context

# Make sure Alembic can import your API modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'API')))

# Import Base and settings **after** adding path
from database import Base       # database.py should contain: Base = declarative_base()
from config import settings     # contains DB credentials

# Alembic Config object
config = context.config

# Set DB URL dynamically
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@"
    f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

# Set up logging
fileConfig(config.config_file_name)

# This is the key line for autogenerate
target_metadata = Base.metadata


# ---------------- Migration Functions ---------------- #

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Run the correct mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()