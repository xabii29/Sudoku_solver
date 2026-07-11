import numpy as np
import pandas as pd
import os

def string_to(question_str):
    valores = ['0' if c == '.' else int(c) for c in question_str]
    matriz = np.array(valores).reshape(9,9)
    return pd.DataFrame(matriz)

def extraer_juegos(file):
    archivo = pd.read_csv(file)
    archivo = archivo['question']
    for i, val in archivo.items():
        juego = string_to(val)
        Carpeta = "Juegos_extraidos"
        os.makedirs(Carpeta, exist_ok=True)
        ruta = os.path.join(Carpeta,f"Juego_{i}.csv")
        juego.to_csv(ruta,index=False,header=False)

extraer_juegos("test.csv")