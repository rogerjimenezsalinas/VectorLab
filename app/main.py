"""VectorLab — Visualizador de campos vectoriales y sistemas hamiltonianos.

Aplicación educativa para Cálculo Diferencial de Varias Variables.
Stack: FastAPI + SQLAlchemy + SymPy/NumPy + Plotly.js
"""
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import models
from .database import engine, get_db
from .schemas import EstudianteRegistro, EstudianteOut, LoginIn, CampoRequest
from .compute import (
    campo_gradiente, campo_hamiltoniano, campo_vectorial_3d, ExpresionInvalida,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VectorLab",
    description="Visualizador de campos vectoriales y funciones hamiltonianas",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).parent / "static"


# ---------------------------------------------------------------- usuarios --
@app.post("/api/registro", response_model=EstudianteOut, status_code=201)
def registrar(datos: EstudianteRegistro, db: Session = Depends(get_db)):
    existe = (
        db.query(models.Estudiante)
        .filter(
            (models.Estudiante.carnet_universitario == datos.carnet_universitario)
            | (models.Estudiante.correo == datos.correo)
        )
        .first()
    )
    if existe:
        raise HTTPException(409, "Ya existe un registro con ese carnet o correo. Usa 'Ingresar'.")
    est = models.Estudiante(**datos.model_dump())
    db.add(est)
    db.commit()
    db.refresh(est)
    return est


@app.post("/api/login", response_model=EstudianteOut)
def login(datos: LoginIn, db: Session = Depends(get_db)):
    est = (
        db.query(models.Estudiante)
        .filter(
            models.Estudiante.carnet_universitario == datos.carnet_universitario,
            models.Estudiante.correo == datos.correo,
        )
        .first()
    )
    if not est:
        raise HTTPException(401, "Carnet o correo incorrectos. Verifica tus datos o regístrate.")
    return est


# ------------------------------------------------------------------ cálculo --
@app.post("/api/campo")
def calcular_campo(req: CampoRequest):
    try:
        if req.tipo == "gradiente":
            if not req.f:
                raise ExpresionInvalida("Debes ingresar f(x, y).")
            return campo_gradiente(req.f, req.rango, req.densidad)

        if req.tipo == "hamiltoniano":
            if not req.f:
                raise ExpresionInvalida("Debes ingresar H(x, y).")
            return campo_hamiltoniano(req.f, req.rango, req.densidad)

        # vectorial3d
        if not (req.P and req.Q and req.R):
            raise ExpresionInvalida("Debes ingresar las tres componentes P, Q y R.")
        return campo_vectorial_3d(req.P, req.Q, req.R, req.rango, req.densidad)

    except ExpresionInvalida as e:
        raise HTTPException(422, str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ----------------------------------------------------------------- frontend --
@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
