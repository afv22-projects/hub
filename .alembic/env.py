import logging
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from src.hub.reflect.db import DBBase
from src.hub.logging_config import init_logging, InterceptHandler

# Configure mappers to register version tables with metadata
from sqlalchemy.orm import configure_mappers

configure_mappers()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with environment variable if present
db_uri = os.environ.get("DB_URI", "sqlite:///./app.db")
config.set_main_option("sqlalchemy.url", db_uri)

# Initialize loguru logging and route alembic/sqlalchemy through it
init_logging(os.environ.get("LOG_LEVEL", "INFO"))
logging.getLogger("alembic").handlers = [InterceptHandler()]
logging.getLogger("alembic").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.engine").handlers = [InterceptHandler()]
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = DBBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
