"""Configuración de base de datos (SQLite por defecto, PostgreSQL vía DATABASE_URL)."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# En Render.com basta definir DATABASE_URL apuntando a PostgreSQL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vectorlab.db")

# Render entrega URLs 'postgres://'; SQLAlchemy 2.x requiere 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
