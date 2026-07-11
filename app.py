import time

import numpy as np
import pandas as pd
import streamlit as st

from sudoku_core import string_a_juego, resolver_pasos, resuelto

st.set_page_config(page_title="Sudoku Solver en vivo", layout="wide")

ARCHIVO_DB = "test.csv"   # una linea por puzzle, 81 caracteres, sin header ni columnas
PUZZLE_DEFAULT = 0


# ------------------------------------------------------------------
# Cargar la base UNA sola vez (cacheado) - con 400k+ filas no queremos
# releerla en cada rerun del script.
# ------------------------------------------------------------------
@st.cache_data
def cargar_base(ruta):
    """Lee test.csv como texto plano: una linea por puzzle, sin columnas ni header."""
    with open(ruta) as f:
        lineas = [linea.strip() for linea in f if linea.strip()]

    # validar longitud; si hay lineas corruptas, las reportamos pero no truena la app
    lineas_validas = []
    lineas_malas = []
    for i, linea in enumerate(lineas):
        if len(linea) == 81:
            lineas_validas.append(linea)
        else:
            lineas_malas.append((i, len(linea)))

    return lineas_validas, lineas_malas


# ------------------------------------------------------------------
# Estado persistente
# ------------------------------------------------------------------
defaults = {
    "juego_original": None,
    "mascara_original": None,
    "puzzle_cargado_num": None,
    "eventos": None,
    "idx": 0,
    "running": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ------------------------------------------------------------------
# Dibujar el tablero
# ------------------------------------------------------------------
COLOR_SQUARE_BLANCO = "#ffffff20"
COLOR_SQUARE_TRANS = "transparent"
COLOR_ACTIVA = "#2b6cb0"

def dibujar_tablero(juego, mascara_original, celda_activa=None):
    html = "<style>"
    html += """
    table.sudoku {border-collapse: collapse; margin: auto;}
    table.sudoku td {
        width: 36px; height: 36px; text-align: center; vertical-align: middle;
        font-size: 18px; font-family: monospace; border: 1px solid #999;
    }
    table.sudoku tr:nth-child(3n+1) td {border-top: 2px solid #333;}
    table.sudoku td:nth-child(3n+1) {border-left: 2px solid #333;}
    table.sudoku tr:last-child td {border-bottom: 2px solid #333;}
    table.sudoku td:last-child {border-right: 2px solid #333;}
    """
    html += "</style><table class='sudoku'>"
    for r in range(9):
        html += "<tr>"
        for c in range(9):
            val = juego[r, c]
            texto = "" if val == 0 else str(val)

            square_r, square_c = r // 3, c // 3
            fondo_square = COLOR_SQUARE_BLANCO if (square_r + square_c) % 2 == 0 else COLOR_SQUARE_TRANS
            negritas = "font-weight:bold;" if mascara_original[r, c] else "font-weight:normal;"
            estilo = f"background-color:{fondo_square}; {negritas}"

            if celda_activa == (r, c):
                estilo = f"background-color:{COLOR_ACTIVA}; color:white; {negritas}"

            html += f"<td style='{estilo}'>{texto}</td>"
        html += "</tr>"
    html += "</table>"
    return html


def reconstruir_estado(juego_original, eventos, hasta_idx):
    juego = juego_original.copy()
    for evento in eventos[:hasta_idx]:
        r, c = evento["row"], evento["col"]
        if evento["accion"] == "retroceso":
            juego[r, c] = 0
        else:
            juego[r, c] = evento["valor"]
    return juego


def cargar_puzzle(lineas, numero):
    """Toma la linea 'numero' (string de 81 caracteres) y arma el tablero 9x9."""
    juego = string_a_juego(lineas[numero])
    st.session_state.juego_original = juego
    st.session_state.mascara_original = juego != 0
    st.session_state.puzzle_cargado_num = numero
    st.session_state.eventos = None
    st.session_state.idx = 0
    st.session_state.running = False


# ------------------------------------------------------------------
# Cargar la base de datos
# ------------------------------------------------------------------
try:
    lineas_validas, lineas_malas = cargar_base(ARCHIVO_DB)
    max_idx = len(lineas_validas) - 1
    db = lineas_validas if lineas_validas else None
except FileNotFoundError:
    db = None
    lineas_malas = []
    max_idx = 0

# precargar un sudoku por default al abrir la app
if db is not None and st.session_state.juego_original is None:
    cargar_puzzle(db, PUZZLE_DEFAULT)


# ------------------------------------------------------------------
# BARRA LATERAL
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Controles")

    if db is None:
        st.error(f"No se encontró '{ARCHIVO_DB}' junto al script.")
        numero = PUZZLE_DEFAULT
    else:
        if lineas_malas:
            st.warning(f"{len(lineas_malas)} líneas no tienen 81 caracteres y se ignoraron.")
        st.subheader("Número de puzzle")
        numero = st.number_input(
            "Elige un puzzle", min_value=0, max_value=max_idx, value=PUZZLE_DEFAULT, step=1,
        )
        st.caption(f"Rango disponible: 0 - {max_idx}")

    st.divider()
    st.subheader("Velocidad")
    velocidad = st.number_input("Pausa entre cuadros (ms)", min_value=0, max_value=2000, value=15, step=5)
    pasos_por_frame = st.number_input("Pasos por cuadro", min_value=1, max_value=1000, value=1, step=1)

    st.divider()
    resolver_click = st.button("▶️ Resolver", type="primary", disabled=(db is None))


# ------------------------------------------------------------------
# Si cambio el numero de puzzle (sin resolver todavia), precargarlo
# ------------------------------------------------------------------
if db is not None and int(numero) != st.session_state.puzzle_cargado_num and not resolver_click:
    cargar_puzzle(db, int(numero))

if resolver_click and db is not None:
    cargar_puzzle(db, int(numero))
    copia = st.session_state.juego_original.copy()
    st.session_state.eventos = list(resolver_pasos(copia))
    st.session_state.idx = 0
    st.session_state.running = True


# ------------------------------------------------------------------
# AREA PRINCIPAL
# ------------------------------------------------------------------
st.title("🧩 Sudoku Solver — en vivo")

col_izq, col_der = st.columns(2)
col_izq.subheader("Puzzle original")
col_der.subheader("Resolviendo...")

if st.session_state.juego_original is None:
    col_izq.info(f"No se pudo cargar ningún puzzle desde '{ARCHIVO_DB}'.")
else:
    # Panel izquierdo: fuera del fragment, no se re-dibuja en cada cuadro
    col_izq.markdown(
        dibujar_tablero(st.session_state.juego_original, st.session_state.mascara_original),
        unsafe_allow_html=True,
    )

    @st.fragment
    def panel_animacion():
        placeholder_der = st.empty()
        placeholder_paso = st.empty()
        placeholder_final = st.empty()

        if st.session_state.eventos is None:
            placeholder_der.markdown(
                dibujar_tablero(st.session_state.juego_original, st.session_state.mascara_original),
                unsafe_allow_html=True,
            )
            return

        eventos = st.session_state.eventos
        total = len(eventos)
        idx = st.session_state.idx

        juego_actual = reconstruir_estado(st.session_state.juego_original, eventos, idx)
        celda_activa = None
        if idx > 0:
            ultimo = eventos[idx - 1]
            celda_activa = (ultimo["row"], ultimo["col"])

        placeholder_der.markdown(
            dibujar_tablero(juego_actual, st.session_state.mascara_original, celda_activa=celda_activa),
            unsafe_allow_html=True,
        )
        placeholder_paso.markdown(f"**Paso:** {idx} / {total}")

        if st.session_state.running and idx < total:
            # Avanzamos evento por evento, pero los "retroceso" (undo del
            # backtracking) se aplican de corrido sin pausar ni redibujar:
            # solo nos detenemos cuando encontramos un avance real (naked,
            # hidden o intento), o cuando ya no quedan mas eventos.
            avanzados_visibles = 0
            nuevo_idx = idx
            while nuevo_idx < total and avanzados_visibles < pasos_por_frame:
                evento_actual = eventos[nuevo_idx]
                nuevo_idx += 1
                if evento_actual["accion"] != "retroceso":
                    avanzados_visibles += 1

            if velocidad > 0:
                time.sleep(velocidad / 1000.0)
            st.session_state.idx = nuevo_idx
            st.rerun()  # dentro de un fragment, esto solo relanza el fragment

        elif st.session_state.running and idx >= total:
            st.session_state.running = False
            juego_final = reconstruir_estado(st.session_state.juego_original, eventos, total)
            if resuelto(juego_final):
                placeholder_final.success(f"¡Resuelto en {total} pasos!")
            else:
                placeholder_final.error("No se pudo resolver — revisa el puzzle de entrada.")

    with col_der:
        panel_animacion()