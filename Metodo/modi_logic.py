import numpy as np


class ModiSolver:
    @staticmethod
    def resolver(costos, oferta, demanda, asignacion_inicial):
        matriz_costos = np.array(costos, dtype=float)
        matriz_costos[np.isnan(matriz_costos)] = 1e6
        asignacion = np.array(asignacion_inicial, dtype=float)
        filas, cols = asignacion.shape
        historial = []

        # 1. Identificar Base Inicial (m + n - 1 celdas)
        basicas = list(zip(*np.where(asignacion > 0)))
        # Completar base si es degenerada
        for r in range(filas):
            for c in range(cols):
                if len(basicas) < (filas + cols - 1):
                    if (r, c) not in basicas:
                        if not ModiSolver._hay_ciclo(basicas + [(r, c)]):
                            basicas.append((r, c))
                else:
                    break

        for iter_num in range(1, 11):
            # --- PASO A: CALCULAR U y V ---
            u, v = np.full(filas, None), np.full(cols, None)
            u[0] = 0.0
            eq_uv = ["u1 = 0 (Semilla)"]

            # Resolver sistema lineal u + v = c para la BASE
            for _ in range(filas + cols):
                for r, c in basicas:
                    costo = matriz_costos[r, c]
                    if u[r] is not None and v[c] is None:
                        v[c] = costo - u[r]
                        eq_uv.append(
                            f"v{c+1} = C{r+1}{c+1} - u{r+1} = {costo} - {u[r]} = {v[c]}"
                        )
                    elif v[c] is not None and u[r] is None:
                        u[r] = costo - v[c]
                        eq_uv.append(
                            f"u{r+1} = C{r+1}{c+1} - v{c+1} = {costo} - {v[c]} = {u[r]}"
                        )

            u_f = np.array([float(x) if x is not None else 0.0 for x in u])
            v_f = np.array([float(x) if x is not None else 0.0 for x in v])

            # --- PASO B: CALCULAR DELTAS ---
            deltas = np.full((filas, cols), None)
            eq_delta = []
            for r in range(filas):
                for c in range(cols):
                    if (r, c) not in basicas:
                        costo = matriz_costos[r, c]
                        if costo < 1e6:
                            d = costo - (u_f[r] + v_f[c])
                            deltas[r, c] = d
                            eq_delta.append(
                                f"Δ{r+1}{c+1} = {costo} - ({u_f[r]} + {v_f[c]}) = {d}"
                            )

            historial.append(
                {
                    "iteracion": iter_num,
                    "subpaso": "Evaluación",
                    "asignacion": asignacion.copy(),
                    "u": u_f,
                    "v": v_f,
                    "deltas": deltas.copy(),
                    "basicas": list(basicas),
                    "ecuaciones_uv": eq_uv,
                    "ecuaciones_delta": eq_delta,
                    "mensaje": f"Iteración {iter_num}: Evaluación de índices.",
                }
            )

            # Verificar optimalidad
            deltas_num = deltas[deltas != None].astype(float)
            if len(deltas_num) == 0 or np.all(deltas_num >= -1e-9):
                historial[-1]["mensaje"] += " ¡SOLUCIÓN ÓPTIMA!"
                break

            # --- PASO C: MEJORAR (CICLO) ---
            idx_entra = np.unravel_index(
                np.nanargmin(deltas.astype(float)), deltas.shape
            )
            ciclo = ModiSolver._obtener_ciclo(basicas, idx_entra)

            # Theta es el mínimo de las posiciones negativas (impares en el ciclo)
            pos_negativas = [ciclo[i] for i in range(1, len(ciclo), 2)]
            valores_negativos = [asignacion[r, c] for (r, c) in pos_negativas]
            theta = min(valores_negativos)

            historial.append(
                {
                    "iteracion": iter_num,
                    "subpaso": "Ciclo",
                    "asignacion": asignacion.copy(),
                    "u": u_f,
                    "v": v_f,
                    "deltas": deltas.copy(),
                    "basicas": list(basicas),
                    "ciclo": ciclo,
                    "theta": float(theta),
                    "entra": idx_entra,
                    "mensaje": f"Mejora: Celda O{idx_entra[0]+1}D{idx_entra[1]+1} entra con θ = {theta}.",
                }
            )

            # ACTUALIZACIÓN REAL DE LA MATRIZ Y LA BASE
            for i, (r, c) in enumerate(ciclo):
                if i % 2 == 0:
                    asignacion[r, c] += theta
                else:
                    asignacion[r, c] -= theta

            # Actualizar la lista de celdas básicas
            basicas.append(idx_entra)
            # Sale de la base la primera celda que se hizo cero en posición negativa
            for p in pos_negativas:
                if asignacion[p] == 0:
                    basicas.remove(p)
                    break

        return historial

    @staticmethod
    def _hay_ciclo(nodos):
        def buscar(camino, buscando_fila):
            curr = camino[-1]
            if len(camino) >= 4:
                if buscando_fila and curr[0] == camino[0][0]:
                    return True
                if not buscando_fila and curr[1] == camino[0][1]:
                    return True
            for p in nodos:
                if p in camino:
                    continue
                if buscando_fila and p[0] == curr[0]:
                    if buscar(camino + [p], False):
                        return True
                if not buscando_fila and p[1] == curr[1]:
                    if buscar(camino + [p], True):
                        return True
            return False

        for p in nodos:
            if buscar([p], True):
                return True
        return False

    @staticmethod
    def _obtener_ciclo(basicas, inicio):
        nodos = basicas + [inicio]

        def buscar(camino, buscando_fila):
            curr = camino[-1]
            if len(camino) >= 4:
                if buscando_fila and curr[0] == inicio[0]:
                    return camino
                if not buscando_fila and curr[1] == inicio[1]:
                    return camino
            for p in nodos:
                if p in camino:
                    continue
                if buscando_fila and p[0] == curr[0]:
                    res = buscar(camino + [p], False)
                    if res:
                        return res
                if not buscando_fila and p[1] == curr[1]:
                    res = buscar(camino + [p], True)
                    if res:
                        return res
            return None

        return buscar([inicio], True)
