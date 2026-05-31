import numpy as np


class EsquinaNoroeste:
    @staticmethod
    def resolver(costos, oferta, demanda):
        """
        Generador que resuelve paso a paso usando Esquina Noroeste.
        """
        # 1. Sanitización
        matriz_rutas = np.array(costos, dtype=float)
        matriz_rutas[np.isnan(matriz_rutas)] = np.inf

        oferta_rest = np.array(oferta, dtype=int)
        demanda_rest = np.array(demanda, dtype=int)
        asignacion = np.zeros_like(matriz_rutas, dtype=int)

        filas, cols = matriz_rutas.shape
        i, j = 0, 0
        paso = 0

        # Estado Inicial
        yield {
            "paso": 0,
            "asignacion": asignacion.copy(),
            "oferta": oferta_rest.copy(),
            "demanda": demanda_rest.copy(),
            "costos": matriz_rutas.copy(),  # Para ver bloqueos
            "seleccion": None,
            "mensaje": "Estado Inicial",
        }

        # 2. Bucle
        while i < filas and j < cols:
            paso += 1
            disp_actual = oferta_rest[i]
            req_actual = demanda_rest[j]
            es_bloqueada = matriz_rutas[i, j] == np.inf

            cantidad = 0
            mensaje = ""

            if es_bloqueada:
                cantidad = 0
                mensaje = f"Celda [{i}, {j}] bloqueada. Saltando."
            else:
                cantidad = min(disp_actual, req_actual)
                mensaje = f"Asignando {cantidad} a [{i}, {j}]"

            # Aplicar cambios
            asignacion[i, j] = cantidad
            oferta_rest[i] -= cantidad
            demanda_rest[j] -= cantidad

            # Guardamos coordenadas actuales antes de movernos
            coord_actual = (i, j)

            # Decisión de movimiento
            if disp_actual <= req_actual:
                i += 1  # Bajamos
            else:
                j += 1  # Derecha

            # Yield del paso
            yield {
                "paso": paso,
                "asignacion": asignacion.copy(),
                "oferta": oferta_rest.copy(),
                "demanda": demanda_rest.copy(),
                "costos": matriz_rutas.copy(),
                "seleccion": coord_actual,  # Para pintar de verde
                "mensaje": mensaje,
            }
