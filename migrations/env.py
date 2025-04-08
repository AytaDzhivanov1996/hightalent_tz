from logging.config import fileConfig
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context

configure = context.config
fileConfig(configure.config_file_name)
target_metadata = SQLModel.metadata

def run_migrations_offline():
    url = configure.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = AsyncConnection(
        create_async_engine(configure.get_main_option("sqlalchemy.url"))
    )

    async with connectable:
        await connectable.run_sync(do_run_migrations)

def do_run_migrations(connection):
    context.configure(
        connection=connection, 
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())