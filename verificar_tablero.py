import copy

def verificar(tablero):
    def es_valido(t, r, c, v):
        for j in range(9):
            if t[r][j] == v: return False
        for i in range(9):
            if t[i][c] == v: return False
        rf=(r//3)*3; rc=(c//3)*3
        for i in range(rf,rf+3):
            for j in range(rc,rc+3):
                if t[i][j] == v: return False
        return True

    # Verificar que el estado actual no tiene contradicciones
    for r in range(9):
        for c in range(9):
            v = tablero[r][c]
            if v != 0:
                tablero[r][c] = 0
                if not es_valido(tablero, r, c, v):
                    tablero[r][c] = v
                    print("CONTRADICCION en fila={} col={} valor={}".format(r, c, v))
                    return False
                tablero[r][c] = v

    # Intentar resolver
    def solver(t):
        for r in range(9):
            for c in range(9):
                if t[r][c] == 0:
                    for v in range(1,10):
                        if es_valido(t,r,c,v):
                            t[r][c]=v
                            if solver(t): return True
                            t[r][c]=0
                    return False
        return True

    copia = copy.deepcopy(tablero)
    if solver(copia):
        print("El tablero TIENE solucion.")
        print("Solucion:")
        for fila in copia:
            print(fila)
        return True
    else:
        print("El tablero NO tiene solucion.")
        return False


# === PEGA AQUI EL TABLERO ACTUAL ===
# Usa 0 para las casillas vacias
tablero = [
    [9, 4, 6, 3, 7, 2, 1, 8, 5],
    [7, 5, 3, 4, 8, 1, 6, 9, 2],
    [2, 1, 8, 6, 5, 9, 4, 3, 7],
    [3, 9, 2, 1, 0, 0, 7, 5, 0],
    [0, 0, 0, 0, 0, 2, 1, 0, 0],
    [0, 8, 1, 0, 2, 5, 0, 0, 3],
    [1, 3, 7, 0, 4, 6, 0, 2, 9],
    [4, 6, 5, 2, 9, 3, 8, 0, 1],
    [8, 2, 9, 7, 1, 0, 0, 6, 0],
]

verificar(tablero)
