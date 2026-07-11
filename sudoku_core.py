"""
Nucleo del solver de sudoku, reescrito como GENERADORES.

En vez de resolver todo de un jalon, cada funcion va cediendo (yield)
un "paso" cada vez que prueba, llena o deshace un valor. Esto permite
que Streamlit vaya pintando el tablero en vivo, paso por paso.

Tablero: numpy array 9x9 de enteros, 0 = vacio.
"""

import numpy as np

TODOS = set(range(1, 10))


def es_valido(juego, fila, col, valor):
    """Revisa si 'valor' puede ir en (fila, col) segun fila/columna/square."""
    if valor in juego[fila, :]:
        return False
    if valor in juego[:, col]:
        return False
    f0, c0 = (fila // 3) * 3, (col // 3) * 3
    if valor in juego[f0:f0+3, c0:c0+3]:
        return False
    return True


def posibles_de(juego, fila, col):
    usados = set(juego[fila, :]) | set(juego[:, col])
    f0, c0 = (fila // 3) * 3, (col // 3) * 3
    usados |= set(juego[f0:f0+3, c0:c0+3].flatten())
    usados.discard(0)
    return TODOS - usados


def celdas_vacias(juego):
    return [(r, c) for r in range(9) for c in range(9) if juego[r, c] == 0]


# ----------------------------------------------------------------------
# FASE LOGICA: naked singles + hidden singles, como paso a paso
# ----------------------------------------------------------------------

def paso_naked_singles(juego):
    """Una pasada de naked singles. Yield un evento por cada celda llenada."""
    cambios = False
    for (r, c) in celdas_vacias(juego):
        posibles = posibles_de(juego, r, c)
        if len(posibles) == 1:
            valor = posibles.pop()
            juego[r, c] = valor
            cambios = True
            yield {"accion": "naked", "row": r, "col": c, "valor": valor}
    return cambios


def _grupos_hidden(juego):
    """Devuelve las listas de celdas vacias agrupadas por fila, columna y square."""
    filas = {i: [] for i in range(9)}
    columnas = {i: [] for i in range(9)}
    squares = {i: [] for i in range(9)}
    for (r, c) in celdas_vacias(juego):
        sq = (r // 3) * 3 + (c // 3)
        filas[r].append((r, c))
        columnas[c].append((r, c))
        squares[sq].append((r, c))
    return filas, columnas, squares


def paso_hidden_singles(juego):
    """Una pasada de hidden singles (fila, columna y square). Yield por cada celda llenada."""
    cambios = False
    filas, columnas, squares = _grupos_hidden(juego)

    for grupo_dict in (filas, columnas, squares):
        for grupo in grupo_dict.values():
            if not grupo:
                continue
            conteo = {}
            posibles_cache = {}
            for (r, c) in grupo:
                p = posibles_de(juego, r, c)
                posibles_cache[(r, c)] = p
                for val in p:
                    conteo.setdefault(val, []).append((r, c))
            for val, celdas_val in conteo.items():
                if len(celdas_val) == 1:
                    r, c = celdas_val[0]
                    if juego[r, c] == 0:
                        juego[r, c] = val
                        cambios = True
                        yield {"accion": "hidden", "row": r, "col": c, "valor": val}
    return cambios


def resolver_logico_pasos(juego):
    """Alterna naked y hidden singles, cediendo cada paso, hasta que ninguno avance."""
    while True:
        avanzo_naked = False
        for evento in paso_naked_singles(juego):
            avanzo_naked = True
            yield evento

        avanzo_hidden = False
        for evento in paso_hidden_singles(juego):
            avanzo_hidden = True
            yield evento

        if not avanzo_naked and not avanzo_hidden:
            break
        if not (juego == 0).any():
            break


# ----------------------------------------------------------------------
# BACKTRACKING iterativo (para poder cederlo paso a paso, con "undo")
# ----------------------------------------------------------------------

def resolver_backtracking_pasos(juego):
    """
    Backtracking iterativo (no recursivo) para poder yield-ear cada intento
    y cada retroceso, y asi animarlo en Streamlit.
    """
    vacias = celdas_vacias(juego)
    n = len(vacias)
    if n == 0:
        return

    ultimo_intento = [0] * n  # ultimo valor probado en esa posicion (0..9)
    pos = 0

    while 0 <= pos < n:
        r, c = vacias[pos]
        valor = ultimo_intento[pos] + 1
        colocado = False

        while valor <= 9:
            if es_valido(juego, r, c, valor):
                juego[r, c] = valor
                ultimo_intento[pos] = valor
                yield {"accion": "intento", "row": r, "col": c, "valor": valor}
                pos += 1
                colocado = True
                break
            valor += 1

        if not colocado:
            ultimo_intento[pos] = 0
            juego[r, c] = 0
            yield {"accion": "retroceso", "row": r, "col": c, "valor": 0}
            pos -= 1

    # si pos == n, quedo resuelto; si pos < 0, no tiene solucion (no deberia pasar
    # con un puzzle valido de sudoku)


def resolver_pasos(juego):
    """Generador principal: logica primero, backtracking si hace falta."""
    yield from resolver_logico_pasos(juego)
    if (juego == 0).any():
        yield from resolver_backtracking_pasos(juego)


def resuelto(juego):
    return not (juego == 0).any()


def string_a_juego(s):
    """Convierte un string de 81 caracteres ('.' o '0' = vacio) en un array 9x9."""
    valores = [0 if ch in ".0" else int(ch) for ch in s.strip()]
    assert len(valores) == 81, f"Se esperaban 81 caracteres, llegaron {len(valores)}"
    return np.array(valores, dtype=int).reshape(9, 9)
