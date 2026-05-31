import numpy as np
import pandas as pd

class HungarianSolver:
    @staticmethod
    def resolver(matriz_original):
        matriz = np.array(matriz_original, dtype=float)
        n = matriz.shape[0]
        pasos = []

        # Estado 0: Matriz Original
        pasos.append({"matriz": matriz.copy(), "mensaje": "Matriz de costos inicial.", "lineas": None})

        # Paso 1: Reducción de Filas
        for i in range(n):
            matriz[i, :] -= np.min(matriz[i, :])
        pasos.append({"matriz": matriz.copy(), "mensaje": "Paso 1: Restar el mínimo de cada fila.", "lineas": None})

        # Paso 2: Reducción de Columnas
        for j in range(n):
            matriz[:, j] -= np.min(matriz[:, j])
        pasos.append({"matriz": matriz.copy(), "mensaje": "Paso 2: Restar el mínimo de cada columna.", "lineas": None})

        # Bucle de optimización (Pasos 3 y 4)
        while True:
            lineas_h, lineas_v = HungarianSolver._calcular_lineas_minimas(matriz)
            num_lineas = len(lineas_h) + len(lineas_v)
            
            pasos.append({
                "matriz": matriz.copy(), 
                "mensaje": f"Paso 3: Cubrir ceros con líneas mínimas. Líneas: {num_lineas}",
                "lineas": {"h": lineas_h, "v": lineas_v}
            })

            if num_lineas >= n:
                break # Solución óptima encontrada

            # Paso 4: Ajuste de Matriz
            matriz = HungarianSolver._ajustar_matriz(matriz, lineas_h, lineas_v)
            pasos.append({"matriz": matriz.copy(), "mensaje": "Paso 4: Ajustar matriz (sumar/restar el mínimo no cubierto).", "lineas": None})

        # Paso Final: Asignación
        asignacion = HungarianSolver._obtener_asignacion(matriz)
        pasos.append({
            "matriz": matriz.copy(), 
            "mensaje": "Solución Óptima Encontrada.", 
            "asignacion": asignacion,
            "lineas": None
        })

        return pasos

    @staticmethod
    def _calcular_lineas_minimas(matriz):
        # Algoritmo simplificado para cubrir ceros
        n = matriz.shape[0]
        temp_matriz = (matriz == 0)
        lineas_h, lineas_v = [], []
        
        while np.any(temp_matriz):
            # Contar ceros por fila y columna
            ceros_f = np.sum(temp_matriz, axis=1)
            ceros_c = np.sum(temp_matriz, axis=0)
            
            if np.max(ceros_f) >= np.max(ceros_c):
                idx = np.argmax(ceros_f)
                lineas_h.append(idx)
                temp_matriz[idx, :] = False
            else:
                idx = np.argmax(ceros_c)
                lineas_v.append(idx)
                temp_matriz[:, idx] = False
        return lineas_h, lineas_v

    @staticmethod
    def _ajustar_matriz(matriz, lh, lv):
        n = matriz.shape[0]
        mask = np.ones((n, n), dtype=bool)
        mask[lh, :] = False
        mask[:, lv] = False
        
        min_no_cubierto = np.min(matriz[mask])
        
        # Restar a no cubiertos
        matriz[mask] -= min_no_cubierto
        # Sumar a intersecciones
        for i in lh:
            for j in lv:
                matriz[i, j] += min_no_cubierto
        return matriz

    @staticmethod
    def _obtener_asignacion(matriz):
        # Busca ceros independientes (Asignación simple)
        n = matriz.shape[0]
        res = np.zeros((n, n), dtype=int)
        temp = (matriz == 0)
        for i in range(n):
            for j in range(n):
                if temp[i, j]:
                    res[i, j] = 1
                    temp[i, :] = False
                    temp[:, j] = False
                    break
        return res