import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("POSTGRES_HOST", "host.docker.internal")
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "ticketbooking")

DATABASE_URL = (f"postgresql://{DB_USER}:{DB_PASSWORD}"f"@{DB_HOST}:{DB_PORT}/{DB_NAME}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=30,
    max_overflow=30,
    pool_timeout=60
)

Sessionlocal = sessionmaker(bind=engine)


def get_db():
    db = Sessionlocal()

    try:
        yield db
    finally:
        db.close()