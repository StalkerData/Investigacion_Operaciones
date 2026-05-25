import numpy as np
import pandas as pd


class BigMSolver:
    def __init__(self, c, A, b, ops, mode="max"):
        """
        c: Coefs función objetivo.
        A: Matriz de restricciones.
        b: Lados derechos (RHS).
        ops: Lista de strings ['<=', '>=', '='] para cada restricción.
        mode: 'max' o 'min'.
        """
        self.c_orig = np.array(c, dtype=float)
        self.A_orig = np.array(A, dtype=float)
        self.b_orig = np.array(b, dtype=float)
        self.ops = ops
        self.mode = mode
        self.M = 10**6  # Valor de la Gran M
        self.history = []

    def solve(self):
        # 1. Identificar variables necesarias
        num_vars = len(self.c_orig)
        num_rest = len(self.b_orig)

        # Listas para rastrear tipos de variables
        slack_vars = []
        surplus_vars = []
        artificial_vars = []

        # Construir nombres de columnas y tipos
        self.col_names = [f"X{i+1}" for i in range(num_vars)]

        # Analizar restricciones para añadir variables
        for i, op in enumerate(self.ops):
            if op == "<=":
                self.col_names.append(f"S{len(slack_vars)+1}")
                slack_vars.append(i)
            elif op == ">=":
                self.col_names.append(f"E{len(surplus_vars)+1}")
                surplus_vars.append(i)
                self.col_names.append(f"A{len(artificial_vars)+1}")
                artificial_vars.append(i)
            elif op == "=":
                self.col_names.append(f"A{len(artificial_vars)+1}")
                artificial_vars.append(i)

        total_cols = len(self.col_names)
        tabla = np.zeros((num_rest + 1, total_cols + 1))

        # 2. Llenar la tabla con coeficientes de restricciones
        current_col = num_vars
        s_count, e_count, a_count = 0, 0, 0
        basis = ["Z"] + [None] * num_rest

        for i in range(num_rest):
            # Coeficientes de variables de decisión
            tabla[i + 1, :num_vars] = self.A_orig[i]
            tabla[i + 1, -1] = self.b_orig[i]

            op = self.ops[i]
            if op == "<=":
                tabla[i + 1, num_vars + s_count + e_count + a_count] = 1
                basis[i + 1] = f"S{s_count+1}"
                s_count += 1
            elif op == ">=":
                # Exceso
                tabla[i + 1, num_vars + s_count + e_count + a_count] = -1
                e_count += 1
                # Artificial
                tabla[i + 1, num_vars + s_count + e_count + a_count] = 1
                basis[i + 1] = f"A{a_count+1}"
                a_count += 1
            elif op == "=":
                # Artificial
                tabla[i + 1, num_vars + s_count + e_count + a_count] = 1
                basis[i + 1] = f"A{a_count+1}"
                a_count += 1

        # 3. Configurar Función Objetivo (Fila Z)
        # Si es MIN, convertimos a MAX multiplicando por -1
        c_work = self.c_orig.copy()
        if self.mode == "min":
            c_work = -c_work

        tabla[0, :num_vars] = -c_work

        # Penalización M para variables artificiales
        # En MAX, restamos M*A (coeficiente en tabla es +M porque es Z - (-M)A = 0)
        # Pero como la tabla usa -C, si penalizamos con -M, en la tabla queda +M.
        for i, name in enumerate(self.col_names):
            if name.startswith("A"):
                tabla[0, i] = self.M

        # 4. AJUSTE CRÍTICO: Hacer que la base sea canónica
        # Las variables artificiales están en la base, su costo en fila Z debe ser 0
        for i in range(1, num_rest + 1):
            if basis[i].startswith("A"):
                # Fila 0 = Fila 0 - (Coeficiente de A en Fila 0) * Fila de la restricción
                coef = tabla[0, np.where(np.array(self.col_names) == basis[i])[0][0]]
                tabla[0, :] -= coef * tabla[i, :]

        # 5. Bucle Simplex (Reutilizando tu lógica)
        iteration = 0
        while True:
            estado_actual = {
                "iteracion": iteration,
                "df": pd.DataFrame(
                    tabla, columns=self.col_names + ["Solución"], index=basis
                ),
                "pivote_info": None,
                "mensaje": "",
            }

            # Buscar pivote
            fila_Z = tabla[0, :-1]
            col_piv = np.argmin(fila_Z)

            if fila_Z[col_piv] >= -1e-9:
                estado_actual["mensaje"] = "Solución Óptima Encontrada"
                estado_actual["solucion"] = self._interpretar(tabla, basis)
                self.history.append(estado_actual)
                break

            # Fila pivote (Razón mínima)
            col_vals = tabla[1:, col_piv]
            rhs = tabla[1:, -1]
            with np.errstate(divide="ignore", invalid="ignore"):
                ratios = rhs / col_vals
            ratios[col_vals <= 0] = np.inf

            if np.all(ratios == np.inf):
                estado_actual["mensaje"] = "Problema no acotado"
                self.history.append(estado_actual)
                break

            fila_piv = np.argmin(ratios) + 1

            estado_actual["pivote_info"] = (fila_piv, col_piv)
            var_entra = self.col_names[col_piv]
            var_sale = basis[fila_piv]
            estado_actual["mensaje"] = f"Entra {var_entra}, Sale {var_sale}"
            self.history.append(estado_actual)

            # Actualizar Tabla
            pivote_val = tabla[fila_piv, col_piv]
            tabla[fila_piv, :] /= pivote_val
            for i in range(tabla.shape[0]):
                if i != fila_piv:
                    tabla[i, :] -= tabla[i, col_piv] * tabla[fila_piv, :]

            basis[fila_piv] = var_entra
            iteration += 1
            if iteration > 50:
                break

        return self.history

    def _interpretar(self, tabla, basis):
        sol = {"Z": tabla[0, -1] if self.mode == "max" else -tabla[0, -1]}
        for name in self.col_names:
            sol[name] = 0.0
        for i, name in enumerate(basis):
            if name != "Z":
                sol[name] = tabla[i, -1]
        return sol
