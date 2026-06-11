# VectorLab — Visualizador de Campos Vectoriales y Funciones Hamiltonianas

Aplicación web educativa para estudiantes de ingeniería que cursan
**Cálculo Diferencial de Varias Variables**. Permite registrarse, escribir una
función de varias variables y explorar su comportamiento en gráficas 3D
interactivas (rotación, zoom y vista desde cualquier dirección).

## Funcionalidades

| Modo | Entrada | Salida |
|------|---------|--------|
| **Campo gradiente** | f(x, y) | Superficie z = f(x,y) + campo ∇f (conos en el plano) + ∂f/∂x, ∂f/∂y simbólicas |
| **Hamiltoniano** | H(x, y) | Superficie de energía + campo X_H = (∂H/∂y, −∂H/∂x) + curvas de nivel (órbitas) |
| **Campo 3D** | F = (P, Q, R) en (x,y,z) | Campo de conos en R³ + divergencia ∇·F y rotacional ∇×F simbólicos |

- **Registro de estudiantes** con: apellidos, nombres, celular, carnet
  universitario, correo electrónico, materia y universidad (persistido en BD).
- **Guía de sintaxis** integrada con ejemplos de un clic (silla de montar,
  paraboloide, péndulo simple, oscilador de Duffing, campo solenoidal, etc.).
- Render de fórmulas en **LaTeX** (MathJax) con las derivadas exactas.

## Arquitectura

```
Navegador (vanilla JS + Plotly.js + MathJax)
        │  JSON / fetch
        ▼
FastAPI (app/main.py)
 ├── /api/registro, /api/login  → SQLAlchemy → SQLite / PostgreSQL
 └── /api/campo                 → SymPy (derivación simbólica + parsing seguro)
                                  NumPy (evaluación vectorizada en malla)
```

**Bondades de Python aprovechadas:** SymPy deriva *exactamente* (no
diferencias finitas) el gradiente, el campo hamiltoniano, la divergencia y el
rotacional; `lambdify` compila las expresiones a funciones NumPy vectorizadas
para evaluar miles de puntos por petición.

**Seguridad del parser:** lista blanca de caracteres y funciones, límite de
longitud, validación de variables libres y manejo de singularidades
(inf/NaN → null). No se ejecuta código arbitrario del usuario.

## Ejecución local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000   (API docs en /docs)
```

## Despliegue en Render.com (Docker)

1. Sube el repositorio a GitHub.
2. En Render: **New → Web Service → Docker** (detecta el `Dockerfile`).
3. Para persistencia real crea una BD PostgreSQL en Render y define la
   variable de entorno `DATABASE_URL` (el código convierte automáticamente
   `postgres://` → `postgresql://`). Si quieres usar PostgreSQL añade
   `psycopg2-binary` a `requirements.txt`.
4. Sin `DATABASE_URL` usa SQLite local (suficiente para pruebas; en el plan
   gratuito de Render el disco es efímero y se pierde en cada redeploy).

## Sintaxis de funciones (resumen)

`x^2` o `x**2` · multiplicación implícita `3x y` · `sin cos tan exp log sqrt abs`
· constantes `pi`, `e` · decimales con punto. Variables: `x, y` (escalar),
`x, y, z` (campo 3D).

## Estructura

```
campos-vectoriales/
├── app/
│   ├── main.py        # rutas FastAPI
│   ├── compute.py     # motor SymPy/NumPy
│   ├── models.py      # ORM Estudiante
│   ├── schemas.py     # validación Pydantic
│   ├── database.py    # SQLite/PostgreSQL
│   └── static/        # index.html, app.css, app.js
├── requirements.txt
├── Dockerfile
└── README.md
```

## Posibles extensiones académicas

- Líneas de flujo (integración numérica con `scipy.integrate.solve_ivp`).
- Historial de funciones por estudiante (tabla adicional).
- Autenticación con contraseña + JWT (mismo patrón que tu sistema SGA).
- Exportación de la escena a PNG (botón nativo de Plotly ya disponible).
