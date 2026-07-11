import numpy as np
import os

All_possible_values = set(np.linspace(1,9,9, dtype=int))

def celda(juego, squares):
    celda = {}
    for square in range(len(squares)):
        for row in range(3):
            for column in range(3):
                Value = squares[square][row][column]
                fila = row + (square//3)*3
                columna = column + (square%3)*3
                celda_idx = fila * 9 + columna
                if Value == 0:
                    possible_values =All_possible_values - set((possible__values_row(juego, fila) 
                                           | possible__values_column(juego, columna) 
                                           | possible_values_square(squares[square])))
                else:
                    possible_values = set()
                celda[celda_idx] = {"Value": Value, 
                            "Square": square, 
                            "Row": fila,
                            "Column": columna,
                            "Possible Values": possible_values
                        }
    return celda

def square(juego):
    square = {}
    for i in range(3):
        for j in range(3):
            square_num = i*3+j
            celda_values = juego.iloc[i*3:(i+1)*3, j*3:(j+1)*3].values
            square[square_num] = celda_values
    return square

def possible__values_row(juego, row):
    row_values = juego.iloc[row, :].values
    return set([x for x in row_values if x != 0])

def possible__values_column(juego, column):
    column_values = juego.iloc[:, column].values
    return set([x for x in column_values if x != 0])

def possible_values_square(square):
    square_values = square.flatten()
    return set([x for x in square_values if x != 0])

def possible_update(celdas,row,col,squa,val):
    for info in celdas.values():
        if info["Row"]==row or info["Column"] == col or info["Square"] == squa:
            info["Possible Values"].discard(val)

def imprimir_juego(juego):
    print("-------------------------","\n")
    for i in range(juego.shape[0]):
        print("|", end=" ")
        for j in range(juego.shape[1]):
            print(juego.iloc[i,j], end=" ")
            if (j+1) % 3 == 0: print("|", end=" ")
        print("\n")
        if (i+2) % 3 == 1: print("-------------------------","\n")

def solver(juego, celdas):
    cambios = False
    for celda_idx, celda_info in celdas.items():
        if celda_info["Value"] == 0 and len(celda_info["Possible Values"]) == 1:
            value_to_fill = celda_info["Possible Values"].pop()
            row = celda_info["Row"]
            column = celda_info["Column"]
            squ = celda_info["Square"]
            juego.iloc[row, column] = value_to_fill
            print(f"Filled cell at row {row}, column {column} with value {value_to_fill}.")
            celda_info["Value"] = value_to_fill
            possible_update(celdas,row,column,squ,value_to_fill)
            cambios = True
    return juego, cambios

def hidden(juego, celdas):
    cambios = False
    for idx, info in celdas.items():
        if info["Possible Values"] == set():
            continue
        
        fila, columna, squ = info["Row"], info["Column"], info["Square"]
        check_squ = info["Possible Values"].copy()
        check_row = info["Possible Values"].copy()
        check_col = info["Possible Values"].copy()
        
        for idx_c, info_c in celdas.items():
            
            if info_c["Possible Values"] == set() or idx == idx_c:
                continue

            if info_c["Square"] == squ:
                check_squ -= info_c["Possible Values"]
            if info_c["Row"] == fila:
                check_row -= info_c["Possible Values"]
            if info_c["Column"] == columna:
                check_col -= info_c["Possible Values"]

        for check in (check_squ, check_row, check_col):
            if  len(check) == 1:
                valor = check.pop()
                juego.iloc[fila, columna] = valor
                print(f"Filled cell at row {fila}, column {columna} with value {valor}.")
                info["Value"]=valor
                info["Possible Values"]=set()
                possible_update(celdas,fila,columna,squ,valor)
                cambios = True
                break
    return juego, cambios
                            
def backtracking(juego, contador = 0):
    for fila in range(9):
        for columna in range(9):
            if juego.iloc[fila,columna]==0:
                contador +=1
                squares = square(juego)
                celdas = celda(juego,squares)
                idx = fila * 9 + columna
                posibles = celdas[idx]["Possible Values"]
                for value in posibles:
                    juego.iloc[fila,columna] = value
                    if backtracking(juego,contador):
                        return True
                    juego.iloc[fila,columna] = 0
                return False
    imprimir_juego(juego)
    print(f"Se resolvio en {contador} pasos de backtracking")
    return True

def resuelto(juego):
    return not (juego==0).any().any()

def logico(juego):
    cambios = True
    while cambios and not resuelto(juego):
        squares = square(juego)
        celdas = celda(juego, squares)
        juego, cambios_single = solver(juego, celdas)
        if cambios_single == True: continue

        squares = square(juego)
        celdas = celda(juego, squares)
        juego, cambios_hidden = hidden(juego, celdas)
        
        cambios = cambios_single or cambios_hidden
    imprimir_juego(juego)

def resolver(juego,carpeta):

    imprimir_juego(juego)
    logico(juego)

    ruta = os.path.join(carpeta,"Solucion.csv")
    if resuelto(juego):
        print("Solucionado")
        juego.to_csv(ruta, index=False, header=False)
    else:
        print("Forzando la solucion\n\n")
        backtracking(juego)
        print("Solucionado")
        juego.to_csv(ruta, index=False, header=False)
    





