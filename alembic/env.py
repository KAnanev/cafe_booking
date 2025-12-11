from alembic import context
from fastapi_users_db_sqlalchemy import GUID
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from src.core.config import settings
from src.core.base import Base

config = context.config

fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.sync_database_url)

target_metadata = Base.metadata


def render_item(obj_type, obj, autogen_context):
    if obj_type == "type" and isinstance(obj, GUID):
        autogen_context.imports.add("from fastapi_users_db_sqlalchemy import GUID")
        return "GUID"
    return False


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
