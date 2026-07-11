import pandas as pd

ruta_bd = "test_orig.csv"
juego = pd.read_csv(ruta_bd)
juego = juego['question']
juego.to_csv("test.csv",index=False,header=False)