
## Este solver utiliza 3 tecnicas para resolver un sudoku.

1. Single naked
    - El metodo single naked evalua las posiciones donde solo es posible un solo valor en las celdas vacias.
2. Single Hidden
    - Sigle Hidden busca valores unicos por cuadrado, donde solo es posible un valor a partir de los valores que son posibles en otras celdas.
3. Backtracking (Brute force)
    - Basicamente se prueban valores hasta que se soluciona el juego.

En la carpeta principal se encuentra una aplición de **Streamlit**
Se ejecuta desde la terminal con el comando "streamlit run app.py"

En la carpeta *sudoku_code*, se ecuentra el codigo para ejecutar el solver en tu maquina sin instalar streamlit.
Se utilizaron DataFrames (nada optimizado, fue por proceso de practica).

El archivo *sudoku_core.py* es el motor de la app de streamlit. Contiene los metodos para resolver los sudokus.

El archivo *test.py* contiene todos los juegos de la base de datos de: https://www.kaggle.com/datasets/bryanpark/sudoku
