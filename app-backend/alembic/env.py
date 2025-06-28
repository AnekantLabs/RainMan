from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup Alembic config
config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Import your Base and all models here ---
from app.core.db_session import Base
from app.models.db_models import Account, Trade, AlertLog, User  # Ensures metadata is populated

# Set metadata for autogeneration
target_metadata = Base.metadata

# Offline migration mode
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# Online migration mode
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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

# Run appropriate migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
