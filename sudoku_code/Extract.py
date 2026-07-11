import numpy as np
import pandas as pd
import os
import random

def string_to(question_str):
    valores = ['0' if c == '.' else int(c) for c in question_str]
    matriz = np.array(valores).reshape(9,9)
    return pd.DataFrame(matriz)

def extraer_juego(file):
    juego = pd.read_csv(file)
    juego = juego['question']
    n = random.choice(range(len(juego)))
    print(f"Se cargo la partida {n} de la base de datos")
    juego = string_to(juego.loc[n])

    Carpeta = "Juegos"
    ruta_carpeta = os.path.join(Carpeta,f"Juego_test_{n}")
    os.makedirs(ruta_carpeta, exist_ok=True)
    
    ruta_juego = os.path.join(ruta_carpeta,f"Juego.csv")
    juego.to_csv(ruta_juego,index=False,header=False)
    return ruta_carpeta
