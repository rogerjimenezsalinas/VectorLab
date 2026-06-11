"""Esquemas Pydantic (validación de entrada/salida)."""
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class EstudianteRegistro(BaseModel):
    apellidos: str = Field(..., min_length=2, max_length=120)
    nombres: str = Field(..., min_length=2, max_length=120)
    celular: str = Field(..., min_length=6, max_length=20)
    carnet_universitario: str = Field(..., min_length=3, max_length=30)
    correo: EmailStr
    materia: str = Field(..., min_length=3, max_length=150)
    universidad: str = Field(..., min_length=3, max_length=150)


class EstudianteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    apellidos: str
    nombres: str
    carnet_universitario: str
    correo: str
    materia: str
    universidad: str


class LoginIn(BaseModel):
    carnet_universitario: str
    correo: EmailStr


class CampoRequest(BaseModel):
    """Petición de visualización.

    tipo:
      - gradiente    : f(x,y)      → superficie z=f + campo ∇f
      - hamiltoniano : H(x,y)      → superficie + campo X_H=(∂H/∂y, -∂H/∂x) + órbitas
      - vectorial3d  : F=(P,Q,R)   → campo de conos en R³
    """
    tipo: Literal["gradiente", "hamiltoniano", "vectorial3d"]
    f: Optional[str] = None          # f(x,y) o H(x,y)
    P: Optional[str] = None          # componente i de F(x,y,z)
    Q: Optional[str] = None          # componente j
    R: Optional[str] = None          # componente k
    rango: float = Field(3.0, gt=0.1, le=20)     # dominio [-rango, rango]
    densidad: int = Field(12, ge=5, le=25)       # puntos por eje para el campo
