import numpy as np


class CostoMinimo:
    @staticmethod
    def resolver(costos, oferta, demanda):
        # 1. Sanitización
        matriz_costos = np.array(costos, dtype=float)
        matriz_costos[np.isnan(matriz_costos)] = np.inf

        oferta_rest = np.array(oferta, dtype=int)
        demanda_rest = np.array(demanda, dtype=int)
        asignacion = np.zeros_like(matriz_costos, dtype=int)

        paso = 0

        # Estado Inicial
        yield {
            "paso": 0,
            "asignacion": asignacion.copy(),
            "oferta": oferta_rest.copy(),
            "demanda": demanda_rest.copy(),
            "costos": matriz_costos.copy(),
            "seleccion": None,
            "mensaje": "Estado Inicial",
        }

        # 2. Bucle
        while oferta_rest.sum() > 0 and demanda_rest.sum() > 0:
            paso += 1

            # Buscar mínimo
            idx_min = np.argmin(matriz_costos)
            i, j = np.unravel_index(idx_min, matriz_costos.shape)
            costo_val = matriz_costos[i, j]

            if costo_val == np.inf:
                yield {
                    "paso": paso,
                    "asignacion": asignacion.copy(),
                    "oferta": oferta_rest.copy(),
                    "demanda": demanda_rest.copy(),
                    "costos": matriz_costos.copy(),
                    "seleccion": None,
                    "mensaje": "Error: Solo quedan rutas bloqueadas.",
                }
                break

            cantidad = min(oferta_rest[i], demanda_rest[j])

            asignacion[i, j] = cantidad
            oferta_rest[i] -= cantidad
            demanda_rest[j] -= cantidad

            # Anulación (Lógica visual: ponemos Infinito donde ya no se puede asignar)
            if oferta_rest[i] == 0 and demanda_rest[j] == 0:
                matriz_costos[:, j] = (
                    np.inf
                )  # Tachamos columna arbitrariamente en empate
            elif oferta_rest[i] == 0:
                matriz_costos[i, :] = np.inf
            else:
                matriz_costos[:, j] = np.inf

            yield {
                "paso": paso,
                "asignacion": asignacion.copy(),
                "oferta": oferta_rest.copy(),
                "demanda": demanda_rest.copy(),
                "costos": matriz_costos.copy(),  # Importante para ver qué se tachó (gris)
                "seleccion": (i, j),
                "mensaje": f"Costo mínimo {costo_val:.0f} en [{i},{j}]. Asignado: {cantidad}",
            }
