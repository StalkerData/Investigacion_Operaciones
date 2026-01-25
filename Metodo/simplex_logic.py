import numpy as np
import pandas as pd

class SimplexSolver:
    def __init__(self, c, A, b):
        """
        c: Coeficientes función objetivo (lista o array)
        A: Matriz de restricciones (lista de listas o array)
        b: Lados derechos (lista o array)
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.num_vars = len(c)
        self.num_restricciones = len(b)
        self.history = [] 
        
        # Nombres de todas las columnas (Variables de decisión + Holgura)
        # Esto nos servirá para saber qué variable entra a la base
        self.col_names = [f"X{i+1}" for i in range(self.num_vars)] + \
                         [f"S{i+1}" for i in range(self.num_restricciones)]

    def solve(self):
        """Ejecuta todo el método simplex y guarda los pasos."""
        # 1. Crear tabla inicial
        tabla = self._crear_tabla_inicial()
        
        # 2. Definir la Base Inicial (Etiquetas de las filas)
        # Inicialmente son Z y las variables de holgura (S1, S2...)
        current_basis = ["Z"] + [f"S{i+1}" for i in range(self.num_restricciones)]
        
        iteration = 0
        while True:
            # Guardar estado actual antes de operar
            # Pasamos 'current_basis' para que el DataFrame tenga las etiquetas correctas
            estado_actual = {
                "iteracion": iteration,
                "tabla": tabla.copy(),
                "df": self._tabla_to_dataframe(tabla, current_basis),
                "pivote_info": None,
                "mensaje": ""
            }

            # 3. Buscar pivote
            col_piv, fila_piv = self._seleccionar_pivote(tabla)

            if col_piv is None:
                estado_actual["mensaje"] = "Solución Óptima Encontrada"
                estado_actual["solucion"] = self._interpretar_solucion(tabla, current_basis)
                self.history.append(estado_actual)
                break
            
            # Guardar info del pivote
            estado_actual["pivote_info"] = (fila_piv, col_piv)
            
            # Identificar nombres para el mensaje
            var_entra = self.col_names[col_piv]
            var_sale = current_basis[fila_piv]
            
            estado_actual["mensaje"] = f"Entra {var_entra} (Col {col_piv+1}) y Sale {var_sale} (Fila {fila_piv})"
            self.history.append(estado_actual)

            # 4. Actualizar tabla (Siguiente iteración)
            tabla = self._actualizar_tabla(tabla, col_piv, fila_piv)
            
            # --- ACTUALIZACIÓN CRÍTICA DE LA BASE ---
            # La variable que entra reemplaza a la que sale en la lista de etiquetas
            current_basis[fila_piv] = var_entra
            
            iteration += 1
            
            if iteration > 100:
                estado_actual["mensaje"] = "Límite de iteraciones alcanzado"
                break

        return self.history

    def _crear_tabla_inicial(self):
        tabla = np.zeros((self.num_restricciones + 1, self.num_vars + self.num_restricciones + 1))
        tabla[1:, :self.num_vars] = self.A
        tabla[1:, self.num_vars:self.num_vars + self.num_restricciones] = np.eye(self.num_restricciones)
        tabla[1:, -1] = self.b
        tabla[0, :self.num_vars] = -self.c
        return tabla

    def _seleccionar_pivote(self, tabla):
        fila_Z = tabla[0, :-1]
        col_pivote = np.argmin(fila_Z)
        
        if fila_Z[col_pivote] >= -1e-9: 
            return None, None

        columna_valores = tabla[1:, col_pivote]
        rhs = tabla[1:, -1]
        
        with np.errstate(divide='ignore', invalid='ignore'):
            cocientes = rhs / columna_valores
            
        cocientes[columna_valores <= 0] = np.inf
        
        if np.all(cocientes == np.inf):
            return None, None 

        fila_pivote = np.argmin(cocientes) + 1
        return col_pivote, fila_pivote

    def _actualizar_tabla(self, tabla, col_piv, fila_piv):
        nueva_tabla = tabla.copy()
        pivote = nueva_tabla[fila_piv, col_piv]
        nueva_tabla[fila_piv, :] /= pivote

        for i in range(nueva_tabla.shape[0]):
            if i != fila_piv:
                nueva_tabla[i, :] -= nueva_tabla[i, col_piv] * nueva_tabla[fila_piv, :]
        
        return nueva_tabla

    def _tabla_to_dataframe(self, tabla, row_labels):
        """
        Convierte la matriz a DataFrame usando las etiquetas de fila dinámicas (Base).
        """
        # Columnas: X1..Xn, S1..Sm, RHS
        cols = self.col_names + ["Solución"]
        
        # Usamos las etiquetas de fila que nos pasan (Z, S1, X2, etc.)
        df = pd.DataFrame(tabla, columns=cols, index=row_labels)
        return df

    def _interpretar_solucion(self, tabla, current_basis):
        """
        Interpreta la solución basándose en las variables que quedaron en la base.
        """
        solucion = {}
        
        # Inicializar todas las variables en 0
        for name in self.col_names:
            solucion[name] = 0.0
            
        # Leer valores de la base
        # current_basis tiene la forma ['Z', 'X1', 'S2'...]
        # tabla[:,-1] tiene los valores RHS
        
        for i, var_name in enumerate(current_basis):
            if var_name == "Z":
                solucion["Z"] = tabla[i, -1]
            else:
                # Asignar el valor del RHS a la variable básica correspondiente
                solucion[var_name] = tabla[i, -1]
        
        return solucion