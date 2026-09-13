from logging.config import fileConfig
from pathlib import Path
import sys

from dotenv import load_dotenv


# ============================================================
# 1. Add project root directory to sys.path
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))


# ============================================================
# 2. Load environment variables BEFORE importing app config
# ============================================================

load_dotenv(BASE_DIR / ".env")


from sqlalchemy import engine_from_config, pool
from alembic import context


# ============================================================
# 3. Import application database configuration
# ============================================================

from app.db.base import Base
from app.db.database import DATABASE_URL


# ============================================================
# 4. Import ALL SQLAlchemy models
#
# These imports are important because they register the models
# with Base.metadata so Alembic can detect schema changes.
# ============================================================

from app.models.user import User
from app.models.venue import Venue
from app.models.seat import Seat
from app.models.event import Event
from app.models.booking import Booking
from app.models.booking_seat import BookingSeat
from app.models.payment import Payment


# ============================================================
# Interpret the config file for Python logging.
# ============================================================

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ============================================================
# 5. DEBUG PRINT
# ============================================================

print("\n==================================================")
print("DEBUG - Alembic is using DATABASE_URL:")
print(DATABASE_URL)
print("==================================================\n")


# ============================================================
# 6. Override alembic.ini URL with application DATABASE_URL
# ============================================================

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL
)


# ============================================================
# 7. Alembic metadata
# ============================================================

target_metadata = Base.metadata


# ============================================================
# OFFLINE MIGRATIONS
# ============================================================

def run_migrations_offline() -> None:
    """Run migrations in offline mode."""

    url = config.get_main_option(
        "sqlalchemy.url"
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# ONLINE MIGRATIONS
# ============================================================

def run_migrations_online() -> None:
    """Run migrations in online mode."""

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# RUN MIGRATION
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

