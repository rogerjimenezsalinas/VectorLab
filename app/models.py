"""Modelos ORM."""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    apellidos = Column(String(120), nullable=False)
    nombres = Column(String(120), nullable=False)
    celular = Column(String(20), nullable=False)
    carnet_universitario = Column(String(30), unique=True, index=True, nullable=False)
    correo = Column(String(150), unique=True, index=True, nullable=False)
    materia = Column(String(150), nullable=False)
    universidad = Column(String(150), nullable=False)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))
