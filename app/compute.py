"""Motor de cálculo: parsing seguro con SymPy y evaluación vectorizada con NumPy.

Aprovecha las "bondades de Python":
  * SymPy   → derivación simbólica exacta (∇f, X_H) y validación de sintaxis.
  * NumPy   → evaluación vectorizada sobre mallas (lambdify).
"""
import re
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

X, Y, Z = sp.symbols("x y z")

_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,  # permite 2x, x y → 2*x, x*y
    convert_xor,                          # permite x^2 → x**2
)

# Lista blanca de funciones permitidas
_LOCALS = {
    "x": X, "y": Y, "z": Z,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "atan2": sp.atan2,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt,
    "abs": sp.Abs, "Abs": sp.Abs,
    "pi": sp.pi, "e": sp.E,
}

# Solo se admiten estos caracteres en la expresión (defensa previa al parser)
_TOKEN_RE = re.compile(r"^[0-9a-zA-Z_+\-*/^().,\s]+$")


class ExpresionInvalida(ValueError):
    pass


def parse_segura(texto: str, simbolos_permitidos: set) -> sp.Expr:
    """Convierte texto a expresión SymPy validando caracteres y símbolos."""
    texto = (texto or "").strip()
    if not texto:
        raise ExpresionInvalida("La expresión está vacía.")
    if len(texto) > 300:
        raise ExpresionInvalida("Expresión demasiado larga (máx. 300 caracteres).")
    if not _TOKEN_RE.match(texto):
        raise ExpresionInvalida("Caracteres no permitidos. Usa solo letras, números y + - * / ^ ( ) .")
    try:
        expr = parse_expr(texto, local_dict=_LOCALS, transformations=_TRANSFORMS, evaluate=True)
    except Exception:
        raise ExpresionInvalida("Sintaxis inválida. Revisa la guía de escritura de funciones.")
    libres = expr.free_symbols
    extranos = {str(s) for s in libres} - {str(s) for s in simbolos_permitidos}
    if extranos:
        raise ExpresionInvalida(
            f"Variables no reconocidas: {', '.join(sorted(extranos))}. "
            f"Solo se permiten: {', '.join(sorted(str(s) for s in simbolos_permitidos))}."
        )
    return expr


def _limpiar(arr: np.ndarray, limite: float = 1e6) -> list:
    """Reemplaza inf/NaN por None (JSON-safe) y recorta magnitudes extremas."""
    arr = np.asarray(arr, dtype=float)
    arr = np.where(np.isfinite(arr), arr, np.nan)
    arr = np.where(np.abs(arr) > limite, np.nan, arr)
    return np.where(np.isnan(arr), None, np.round(arr, 6)).tolist()


def campo_gradiente(f_txt: str, rango: float, densidad: int) -> dict:
    """Superficie z = f(x,y) + campo gradiente ∇f sobre el plano xy."""
    f = parse_segura(f_txt, {X, Y})
    fx, fy = sp.diff(f, X), sp.diff(f, Y)

    f_n = sp.lambdify((X, Y), f, "numpy")
    fx_n = sp.lambdify((X, Y), fx, "numpy")
    fy_n = sp.lambdify((X, Y), fy, "numpy")

    # Malla fina para la superficie
    g = np.linspace(-rango, rango, 60)
    GX, GY = np.meshgrid(g, g)
    with np.errstate(all="ignore"):
        GZ = np.broadcast_to(np.asarray(f_n(GX, GY), dtype=float), GX.shape)

    # Malla gruesa para los vectores
    q = np.linspace(-rango, rango, densidad)
    QX, QY = np.meshgrid(q, q)
    with np.errstate(all="ignore"):
        U = np.broadcast_to(np.asarray(fx_n(QX, QY), dtype=float), QX.shape)
        V = np.broadcast_to(np.asarray(fy_n(QX, QY), dtype=float), QX.shape)

    return {
        "tipo": "gradiente",
        "latex": {"f": sp.latex(f), "fx": sp.latex(fx), "fy": sp.latex(fy)},
        "superficie": {"x": _limpiar(g), "y": _limpiar(g), "z": _limpiar(GZ)},
        "campo": {
            "x": _limpiar(QX.ravel()), "y": _limpiar(QY.ravel()),
            "u": _limpiar(U.ravel()), "v": _limpiar(V.ravel()),
        },
    }


def campo_hamiltoniano(h_txt: str, rango: float, densidad: int) -> dict:
    """Sistema hamiltoniano: ẋ = ∂H/∂y, ẏ = -∂H/∂x.

    Devuelve la superficie de energía H(x,y), el campo X_H y curvas de nivel
    (órbitas: H = const por conservación de la energía).
    """
    H = parse_segura(h_txt, {X, Y})
    Hx, Hy = sp.diff(H, X), sp.diff(H, Y)

    H_n = sp.lambdify((X, Y), H, "numpy")
    Hx_n = sp.lambdify((X, Y), Hx, "numpy")
    Hy_n = sp.lambdify((X, Y), Hy, "numpy")

    g = np.linspace(-rango, rango, 70)
    GX, GY = np.meshgrid(g, g)
    with np.errstate(all="ignore"):
        GZ = np.broadcast_to(np.asarray(H_n(GX, GY), dtype=float), GX.shape)

    q = np.linspace(-rango, rango, densidad)
    QX, QY = np.meshgrid(q, q)
    with np.errstate(all="ignore"):
        U = np.broadcast_to(np.asarray(Hy_n(QX, QY), dtype=float), QX.shape)   #  ∂H/∂y
        V = np.broadcast_to(-np.asarray(Hx_n(QX, QY), dtype=float), QX.shape)  # -∂H/∂x

    return {
        "tipo": "hamiltoniano",
        "latex": {
            "H": sp.latex(H),
            "xdot": sp.latex(Hy),
            "ydot": sp.latex(sp.simplify(-Hx)),
        },
        "superficie": {"x": _limpiar(g), "y": _limpiar(g), "z": _limpiar(GZ)},
        "campo": {
            "x": _limpiar(QX.ravel()), "y": _limpiar(QY.ravel()),
            "u": _limpiar(U.ravel()), "v": _limpiar(V.ravel()),
        },
    }


def campo_vectorial_3d(p_txt: str, q_txt: str, r_txt: str, rango: float, densidad: int) -> dict:
    """Campo F(x,y,z) = P i + Q j + R k visualizado con conos 3D.

    Incluye la divergencia y el rotacional simbólicos como apoyo didáctico.
    """
    simbolos = {X, Y, Z}
    P = parse_segura(p_txt, simbolos)
    Q = parse_segura(q_txt, simbolos)
    R = parse_segura(r_txt, simbolos)

    div = sp.simplify(sp.diff(P, X) + sp.diff(Q, Y) + sp.diff(R, Z))
    rot = (
        sp.simplify(sp.diff(R, Y) - sp.diff(Q, Z)),
        sp.simplify(sp.diff(P, Z) - sp.diff(R, X)),
        sp.simplify(sp.diff(Q, X) - sp.diff(P, Y)),
    )

    P_n = sp.lambdify((X, Y, Z), P, "numpy")
    Q_n = sp.lambdify((X, Y, Z), Q, "numpy")
    R_n = sp.lambdify((X, Y, Z), R, "numpy")

    d = min(densidad, 10)  # 10³ = 1000 conos máx. (rendimiento del navegador)
    g = np.linspace(-rango, rango, d)
    GX, GY, GZ = np.meshgrid(g, g, g)
    with np.errstate(all="ignore"):
        U = np.broadcast_to(np.asarray(P_n(GX, GY, GZ), dtype=float), GX.shape)
        V = np.broadcast_to(np.asarray(Q_n(GX, GY, GZ), dtype=float), GX.shape)
        W = np.broadcast_to(np.asarray(R_n(GX, GY, GZ), dtype=float), GX.shape)

    return {
        "tipo": "vectorial3d",
        "latex": {
            "P": sp.latex(P), "Q": sp.latex(Q), "R": sp.latex(R),
            "div": sp.latex(div),
            "rot": [sp.latex(c) for c in rot],
        },
        "campo3d": {
            "x": _limpiar(GX.ravel()), "y": _limpiar(GY.ravel()), "z": _limpiar(GZ.ravel()),
            "u": _limpiar(U.ravel()), "v": _limpiar(V.ravel()), "w": _limpiar(W.ravel()),
        },
    }
