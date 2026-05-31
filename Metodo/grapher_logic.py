import numpy as np
import itertools

class GrapherLogic:
    @staticmethod
    def hallar_intersecciones_puras(A, b):
        """
        Halla únicamente los puntos donde las restricciones se cruzan entre sí.
        No incluye los cortes con los ejes X o Y.
        """
        num_rest = len(b)
        puntos = []
        
        if num_rest < 2:
            return []

        # Combinamos las restricciones de 2 en 2
        for i, j in itertools.combinations(range(num_rest), 2):
            matriz_2x2 = A[[i, j]]
            vector_2 = b[[i, j]]
            
            try:
                # Resolver el sistema de ecuaciones para encontrar el cruce
                punto = np.linalg.solve(matriz_2x2, vector_2)
                
                # Solo consideramos puntos en el primer cuadrante (X1, X2 >= 0)
                # por la naturaleza de la mayoría de problemas de IO
                if punto[0] >= -1e-9 and punto[1] >= -1e-9:
                    puntos.append(tuple(np.round(punto, 4)))
            except np.linalg.LinAlgError:
                # Las líneas son paralelas o coincidentes
                continue
                
        # Retornar lista sin duplicados
        return list(set(puntos))

    @staticmethod
    def es_factible(punto, A, b, ops):
        """Verifica si un punto cumple con todas las restricciones del sistema."""
        for i in range(len(b)):
            valor = np.dot(A[i], punto)
            # Margen de error pequeño para cálculos de punto flotante
            if ops[i] == "<=" and valor > b[i] + 1e-7: return False
            if ops[i] == ">=" and valor < b[i] - 1e-7: return False
            if ops[i] == "=" and not np.isclose(valor, b[i]): return False
        return True