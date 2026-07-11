from solver import *
from Extract import *
import time

t_inicial = time.perf_counter()
ruta_bd = "test.csv"
carpeta = extraer_juego(ruta_bd)
juego = os.path.join(carpeta,"Juego.csv")
juego = pd.read_csv(juego, header=None)

resolver(juego,carpeta)
tiempo = time.perf_counter() - t_inicial
print(f"Tardo {tiempo:.2f} segundos en resolverse")