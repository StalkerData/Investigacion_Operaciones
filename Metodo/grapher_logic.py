import numpy as np
import itertools

class GrapherLogic:
    @staticmethod
    def hallar_intersecciones(A, b):
        num_rest = len(b)
        puntos = []
        
        # Añadir ejes X1=0 y X2=0
        A_ext = np.vstack([A, [[1, 0], [0, 1]]])
        b_ext = np.append(b, [0, 0])
        
        for i, j in itertools.combinations(range(len(b_ext)), 2):
            try:
                matriz_2x2 = A_ext[[i, j]]
                vector_2 = b_ext[[i, j]]
                punto = np.linalg.solve(matriz_2x2, vector_2)
                # Solo primer cuadrante
                if punto[0] >= -1e-7 and punto[1] >= -1e-7:
                    puntos.append(tuple(np.round(punto, 4)))
            except np.linalg.LinAlgError:
                continue
        return list(set(puntos))

    @staticmethod
    def es_factible(punto, A, b, ops):
        for i in range(len(b)):
            valor = np.dot(A[i], punto)
            if ops[i] == "<=" and valor > b[i] + 1e-7: return False
            if ops[i] == ">=" and valor < b[i] - 1e-7: return False
            if ops[i] == "=" and not np.isclose(valor, b[i], atol=1e-7): return False
        return True