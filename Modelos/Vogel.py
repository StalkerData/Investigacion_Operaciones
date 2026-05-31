import numpy as np


class Vogel:
    @staticmethod
    def calcular_penalizaciones(matriz):
        filas, cols = matriz.shape
        pen_filas = np.full(filas, -1.0)
        pen_cols = np.full(cols, -1.0)

        # Filas
        filas_ord = np.sort(matriz, axis=1)
        for i in range(filas):
            if filas_ord[i, 0] == np.inf:
                continue
            if filas_ord[i, 1] == np.inf:
                pen_filas[i] = filas_ord[i, 0]
            else:
                pen_filas[i] = filas_ord[i, 1] - filas_ord[i, 0]

        # Columnas
        cols_ord = np.sort(matriz, axis=0)
        for j in range(cols):
            if cols_ord[0, j] == np.inf:
                continue
            if cols_ord[1, j] == np.inf:
                pen_cols[j] = cols_ord[0, j]
            else:
                pen_cols[j] = cols_ord[1, j] - cols_ord[0, j]

        return pen_filas, pen_cols

    @classmethod
    def resolver(cls, costos, oferta, demanda):
        # 1. Sanitización
        matriz_costos = np.array(costos, dtype=float)
        matriz_costos[np.isnan(matriz_costos)] = np.inf

        oferta_rest = np.array(oferta, dtype=int)
        demanda_rest = np.array(demanda, dtype=int)
        asignacion = np.zeros_like(matriz_costos, dtype=int)

        paso = 0

        # Estado Inicial (Calculamos penalizaciones iniciales para mostrar)
        pf, pc = cls.calcular_penalizaciones(matriz_costos)

        yield {
            "paso": 0,
            "asignacion": asignacion.copy(),
            "oferta": oferta_rest.copy(),
            "demanda": demanda_rest.copy(),
            "costos": matriz_costos.copy(),
            "penalizaciones": {"filas": pf.copy(), "cols": pc.copy()},
            "seleccion": None,
            "mensaje": "Estado Inicial",
        }

        # 2. Bucle
        while oferta_rest.sum() > 0 and demanda_rest.sum() > 0:
            paso += 1

            # Calcular Penalizaciones
            pen_filas, pen_cols = cls.calcular_penalizaciones(matriz_costos)

            # Decisión
            max_pf = np.max(pen_filas)
            max_pc = np.max(pen_cols)

            if max_pf == -1 and max_pc == -1:
                break  # No hay más movimientos posibles

            idx_fila, idx_col = -1, -1

            if max_pf >= max_pc:
                idx_fila = np.argmax(pen_filas)
                idx_col = np.argmin(matriz_costos[idx_fila, :])
            else:
                idx_col = np.argmax(pen_cols)
                idx_fila = np.argmin(matriz_costos[:, idx_col])

            costo_val = matriz_costos[idx_fila, idx_col]
            if costo_val == np.inf:
                break

            # Asignación
            cantidad = min(oferta_rest[idx_fila], demanda_rest[idx_col])
            asignacion[idx_fila, idx_col] = cantidad
            oferta_rest[idx_fila] -= cantidad
            demanda_rest[idx_col] -= cantidad

            # Anulación
            if oferta_rest[idx_fila] == 0 and demanda_rest[idx_col] == 0:
                matriz_costos[:, idx_col] = np.inf
            elif oferta_rest[idx_fila] == 0:
                matriz_costos[idx_fila, :] = np.inf
            else:
                matriz_costos[:, idx_col] = np.inf

            yield {
                "paso": paso,
                "asignacion": asignacion.copy(),
                "oferta": oferta_rest.copy(),
                "demanda": demanda_rest.copy(),
                "costos": matriz_costos.copy(),
                "penalizaciones": {"filas": pen_filas.copy(), "cols": pen_cols.copy()},
                "seleccion": (idx_fila, idx_col),
                "mensaje": f"Max Pen. Asignando {cantidad} a [{idx_fila}, {idx_col}]",
            }
