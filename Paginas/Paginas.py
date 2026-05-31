import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- IMPORTACIONES DE MODELOS ---
# Transporte
from Modelos.CostoMinimo import CostoMinimo
from Modelos.EsquinaNoroeste import EsquinaNoroeste
from Modelos.Vogel import Vogel

# Simplex
from Metodo.simplex_logic import SimplexSolver
from Metodo.big_m_logic import BigMSolver
from Metodo.grapher_logic import GrapherLogic
from Metodo.hungarian_logic import HungarianSolver
from Metodo.modi_logic import ModiSolver


class UI:
    def __init__(self):
        self.inicializar_estado()

    def inicializar_estado(self):
        # --- ESTADO GLOBAL DE NAVEGACIÓN ---
        if "seccion_app" not in st.session_state:
            st.session_state.seccion_app = "Home"

        # --- ESTADO TRANSPORTE ---
        if "pagina" not in st.session_state:
            st.session_state.pagina = "Menu"
        if "algoritmo" not in st.session_state:
            st.session_state.algoritmo = None
        if "dimensiones" not in st.session_state:
            st.session_state.dimensiones = (3, 3)
        if "matriz_costos" not in st.session_state:
            st.session_state.matriz_costos = pd.DataFrame()
        if "oferta" not in st.session_state:
            st.session_state.oferta = pd.DataFrame()
        if "demanda" not in st.session_state:
            st.session_state.demanda = pd.DataFrame()
        if "historial_pasos" not in st.session_state:
            st.session_state.historial_pasos = []
        if "paso_actual" not in st.session_state:
            st.session_state.paso_actual = 0
        if "costos_originales_clean" not in st.session_state:
            st.session_state.costos_originales_clean = None

        # --- ESTADO SIMPLEX ---
        if "simplex_page" not in st.session_state:
            st.session_state["simplex_page"] = 1
        if "num_vars" not in st.session_state:
            st.session_state["num_vars"] = 2
        if "num_rest" not in st.session_state:
            st.session_state["num_rest"] = 2
        if "solver_history" not in st.session_state:
            st.session_state["solver_history"] = None
        if "current_step" not in st.session_state:
            st.session_state["current_step"] = 0

        # --- OTROS MÓDULOS ---
        if "grapher_page" not in st.session_state:
            st.session_state.grapher_page = 1
        if "hungaro_page" not in st.session_state:
            st.session_state.hungaro_page = 1

        # --- ESTADO MODI (NUEVO) ---
        if "modi_page" not in st.session_state:
            st.session_state.modi_page = 1
        if "modi_costos" not in st.session_state:
            st.session_state.modi_costos = pd.DataFrame()
        if "modi_oferta" not in st.session_state:
            st.session_state.modi_oferta = pd.DataFrame()
        if "modi_demanda" not in st.session_state:
            st.session_state.modi_demanda = pd.DataFrame()
        if "modi_pasos" not in st.session_state:
            st.session_state.modi_pasos = []
        if "modi_paso_actual" not in st.session_state:
            st.session_state.modi_paso_actual = 0
        if "modi_costos_orig" not in st.session_state:
            st.session_state.modi_costos_orig = None

    # --- NAVEGACIÓN GLOBAL ---
    def ir_a_home(self):
        st.session_state.seccion_app = "Home"
        st.rerun()

    def ir_a_transporte(self):
        st.session_state.seccion_app = "Transporte"
        st.session_state.pagina = "Menu"
        st.rerun()

    def ir_a_simplex(self):
        st.session_state.seccion_app = "Simplex"
        st.session_state.simplex_page = 1
        st.rerun()

    # =========================================================================
    # SECCIÓN 1: HOME (PANTALLA PRINCIPAL)
    # =========================================================================
    def mostrar_home(self):
        st.title("🚛 Investigación de Operaciones (IO)")
        st.markdown("""
        **Bienvenido.**
        Esta aplicación permite resolver problemas de transporte mediante algoritmos clásicos de Investigación de Operaciones, 
        también métodos de optimización de costo como el Simplex.
        
        *   **Autor:** StalkerData 
        *   **Versión:** 1.8.0
        *   **Tecnología:** Python + NumPy + Streamlit
        *   **Github:** [https://github.com/StalkerData](https://github.com/StalkerData)
        """)

        st.info("Seleccione el módulo que desea utilizar:")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button(
                "📈 Graficadora Lineal", type="primary", use_container_width=True
            ):
                st.session_state.seccion_app = "Grapher"
                st.session_state.grapher_page = 1
                st.rerun()
        with col2:
            if st.button("📐 Método Simplex", type="primary", use_container_width=True):
                self.ir_a_simplex()
        with col3:
            if st.button(
                "🚚 Métodos de Transporte", type="primary", use_container_width=True
            ):
                self.ir_a_transporte()
        with col4:
            if st.button("🎭 Método Húngaro", type="primary", use_container_width=True):
                st.session_state.seccion_app = "Hungaro"
                st.session_state.hungaro_page = 1
                st.rerun()
        with col5:
            if st.button(
                "🔄 Optimización MODI", type="primary", use_container_width=True
            ):
                st.session_state.seccion_app = "Modi"
                st.session_state.modi_page = 1
                st.rerun()

    # =========================================================================
    # SECCIÓN 2: MÓDULO OPTIMIZACIÓN LINEAL (SIMPLEX & GRAN M)
    # =========================================================================
    def simplex_navegar(self, page_num):
        st.session_state["simplex_page"] = page_num
        st.rerun()

    # --- PÁGINA 1: SELECCIÓN DE MÉTODO ---
    def mostrar_simplex_seleccion(self):
        st.title("📐 Módulo de Optimización Lineal")
        st.write("Seleccione el método que desea utilizar:")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Simplex Clásico")
            st.write(
                "Para problemas estándar de **Maximización** con restricciones **≤**."
            )
            if st.button("Elegir Simplex Clásico", use_container_width=True):
                st.session_state.simplex_type = "Clasico"
                st.session_state.simplex_mode = "max"
                self.simplex_navegar(1.5)  # Ir a Configuración

        with col2:
            st.subheader("Método de la Gran M")
            st.write(
                "Para problemas de **Max/Min** con cualquier restricción (≤, ≥, =)."
            )
            if st.button("Elegir Gran M", use_container_width=True):
                st.session_state.simplex_type = "BigM"
                self.simplex_navegar(1.5)  # Ir a Configuración

        if st.button("🏠 Volver al Inicio"):
            self.ir_a_home()

    # --- PÁGINA 1.5: CONFIGURACIÓN (VARS Y REST) ---
    def mostrar_simplex_config(self):
        tipo = st.session_state.get("simplex_type", "Clasico")
        st.title(
            f"⚙️ Configuración: {'Simplex Clásico' if tipo == 'Clasico' else 'Gran M'}"
        )

        if tipo == "BigM":
            mode = st.radio(
                "Objetivo del modelo:", ["Maximizar", "Minimizar"], horizontal=True
            )
            st.session_state["simplex_mode"] = "max" if mode == "Maximizar" else "min"
        else:
            st.info("El Simplex Clásico está configurado para Maximización (Estándar).")
            st.session_state["simplex_mode"] = "max"

        col1, col2 = st.columns(2)
        with col1:
            st.session_state["num_vars"] = st.number_input(
                "Número de Variables (Xn)", 1, 10, st.session_state.get("num_vars", 2)
            )
        with col2:
            st.session_state["num_rest"] = st.number_input(
                "Número de Restricciones", 1, 10, st.session_state.get("num_rest", 2)
            )

        st.write("")
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("⬅️ Atrás"):
                self.simplex_navegar(1)
        with c2:
            if st.button("Crear Modelo ➡️", type="primary"):
                self.simplex_navegar(2)

    # --- PÁGINA 2: INGRESO DE DATOS (ADAPTATIVO) ---
    def mostrar_simplex_ingreso(self):
        tipo = st.session_state.get("simplex_type", "Clasico")
        modo = st.session_state.get("simplex_mode", "max")
        num_vars = st.session_state["num_vars"]
        num_rest = st.session_state["num_rest"]

        st.title(
            f"📝 Definición: {'Simplex Clásico' if tipo == 'Clasico' else 'Gran M'}"
        )
        label_z = "Maximizar Z" if modo == "max" else "Minimizar Z"

        with st.form("simplex_form"):
            st.subheader(f"Función Objetivo ({label_z})")
            cols_z = st.columns(num_vars)
            coef_z = []
            for i in range(num_vars):
                with cols_z[i]:
                    val = st.number_input(
                        f"X{i+1}", key=f"z_{i}", value=0.0, format="%.2f"
                    )
                    coef_z.append(val)

            st.divider()
            st.subheader("Restricciones (Sujeto a:)")

            matrix_a, vector_b, ops = [], [], []

            for i in range(num_rest):
                st.markdown(f"**Restricción {i+1}**")
                cols_r = st.columns(num_vars + 2)
                row_coeffs = []

                for j in range(num_vars):
                    with cols_r[j]:
                        val = st.number_input(
                            f"Coef X{j+1}",
                            key=f"r_{i}_{j}",
                            value=0.0,
                            label_visibility="collapsed",
                            format="%.2f",
                        )
                        st.caption(f"X{j+1}")
                        row_coeffs.append(val)

                # --- LÓGICA DE OPERADOR ---
                with cols_r[num_vars]:
                    if tipo == "Clasico":
                        st.markdown("### ≤")
                        ops.append("<=")
                    else:
                        op = st.selectbox(
                            "Op",
                            ["<=", ">=", "="],
                            key=f"op_{i}",
                            label_visibility="collapsed",
                        )
                        ops.append(op)

                with cols_r[num_vars + 1]:
                    rhs = st.number_input(
                        "RHS",
                        key=f"rhs_{i}",
                        value=0.0,
                        label_visibility="collapsed",
                        format="%.2f",
                    )
                    st.caption("Límite")
                    vector_b.append(rhs)

                matrix_a.append(row_coeffs)

            st.divider()
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.form_submit_button("⬅️ Regresar"):
                    self.simplex_navegar(1.5)
            with c2:
                if st.form_submit_button("Limpiar"):
                    st.rerun()
            with c3:
                solve_clicked = st.form_submit_button(
                    "Resolver y Ver Tabla 🚀", type="primary"
                )

        if solve_clicked:
            if tipo == "Clasico":
                solver = SimplexSolver(coef_z, matrix_a, vector_b)
            else:
                solver = BigMSolver(coef_z, matrix_a, vector_b, ops, mode=modo)

            st.session_state["solver_history"] = solver.solve()
            st.session_state["current_step"] = 0
            self.simplex_navegar(3)

    # --- PÁGINA 3: RESULTADOS (COMÚN PARA AMBOS) ---
    def mostrar_simplex_resultados(self):
        st.title("📊 Iteraciones")
        history = st.session_state["solver_history"]
        curr = st.session_state["current_step"]
        total_steps = len(history)
        step_data = history[curr]

        st.progress((curr + 1) / total_steps)
        st.caption(f"Iteración {step_data['iteracion']} de {total_steps - 1}")

        if "Solución Óptima" in step_data["mensaje"]:
            st.success(f"🎉 {step_data['mensaje']}")
        else:
            st.info(f"ℹ️ {step_data['mensaje']}")

        df = step_data["df"]
        if step_data["pivote_info"]:
            fila_idx, col_idx = step_data["pivote_info"]

            def highlight_pivot(x):
                style_pivote = (
                    "background-color: #ffeb3b; color: black; font-weight: bold;"
                )
                style_relacionado = "background-color: #90caf9; color: black;"
                df_styler = pd.DataFrame("", index=x.index, columns=x.columns)
                df_styler.iloc[fila_idx, :] = style_relacionado
                df_styler.iloc[:, col_idx] = style_relacionado
                df_styler.iloc[fila_idx, col_idx] = style_pivote
                return df_styler

            st.dataframe(
                df.style.apply(highlight_pivot, axis=None).format("{:.2f}"),
                use_container_width=True,
            )
        else:
            st.dataframe(df.style.format("{:.2f}"), use_container_width=True)

        if "solucion" in step_data:
            st.divider()
            st.subheader("🏆 Resultados Finales")
            sol = step_data["solucion"]
            sc1, sc2 = st.columns(2)
            with sc1:
                st.metric("Valor Óptimo (Z)", f"{sol['Z']:.4f}")
            with sc2:
                st.write("Variables de Decisión:")
                for k, v in sol.items():
                    if (
                        k != "Z"
                        and not k.startswith("S")
                        and not k.startswith("A")
                        and not k.startswith("E")
                    ):
                        st.write(f"**{k}** = {v:.4f}")

        st.divider()
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("🏠 Inicio App"):
                self.ir_a_home()
        with b2:
            if st.button("⬅️ Editar Datos"):
                self.simplex_navegar(2)
        with b3:
            if curr > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state["current_step"] -= 1
                    st.rerun()
        with b4:
            if curr < total_steps - 1:
                if st.button("Siguiente ➡️", type="primary"):
                    st.session_state["current_step"] += 1
                    st.rerun()

    # =========================================================================
    # SECCIÓN 3: MÓDULO TRANSPORTE
    # =========================================================================
    def transporte_navegar(self, pagina):
        st.session_state.pagina = pagina
        st.rerun()

    def ejecutar_resolucion_transporte(self):
        algo = st.session_state.algoritmo
        costos = st.session_state.matriz_costos.values.astype(float)
        oferta = st.session_state.oferta.values.flatten()
        demanda = st.session_state.demanda.values.flatten()
        costos_clean = costos.copy()
        costos_clean[np.isnan(costos_clean)] = np.inf
        st.session_state.costos_originales_clean = costos_clean

        generador = None
        if algo == "Noroeste":
            generador = EsquinaNoroeste.resolver(costos, oferta, demanda)
        elif algo == "CostoMinimo":
            generador = CostoMinimo.resolver(costos, oferta, demanda)
        elif algo == "Vogel":
            generador = Vogel.resolver(costos, oferta, demanda)

        if generador:
            st.session_state.historial_pasos = list(generador)
            st.session_state.paso_actual = 0

    def mostrar_menu_transporte(self):
        st.header("Métodos de Transporte")
        c1, c2, c3 = st.columns(3)
        if c1.button("Esquina Noroeste", use_container_width=True):
            st.session_state.algoritmo = "Noroeste"
            self.transporte_navegar("Modelo")
        if c2.button("Costo Mínimo", use_container_width=True):
            st.session_state.algoritmo = "CostoMinimo"
            self.transporte_navegar("Modelo")
        if c3.button("Aproximación de Vogel", use_container_width=True):
            st.session_state.algoritmo = "Vogel"
            self.transporte_navegar("Modelo")
        if st.button("🏠 Volver al Inicio"):
            self.ir_a_home()

    def mostrar_modelo_transporte(self):
        st.header(f"Configuración: {st.session_state.algoritmo}")
        c1, c2 = st.columns(2)
        filas = c1.number_input("Filas", 2, 20, 3)
        cols = c2.number_input("Columnas", 2, 20, 4)
        c_btn1, c_btn2 = st.columns([1, 4])
        if c_btn1.button("⬅ Menú"):
            self.transporte_navegar("Menu")
        if c_btn2.button("Construir Matriz 🏗️", type="primary"):
            st.session_state.dimensiones = (filas, cols)
            cols_names = [f"X{j+1}" for j in range(cols)]
            st.session_state.matriz_costos = pd.DataFrame(
                np.nan, index=range(filas), columns=cols_names
            )
            st.session_state.oferta = pd.DataFrame(
                0, index=range(filas), columns=["Fabricado"]
            )
            st.session_state.demanda = pd.DataFrame(
                0, index=["Demanda"], columns=cols_names
            )
            for key in ["editor_costos", "editor_oferta", "editor_demanda"]:
                if key in st.session_state:
                    del st.session_state[key]
            self.transporte_navegar("Matriz")

    def mostrar_matriz_transporte(self):
        st.header("Ingreso de Datos")
        filas, cols = st.session_state.dimensiones
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Costos")
            df_costos = st.data_editor(
                st.session_state.matriz_costos,
                key="editor_costos",
                height=300,
                use_container_width=True,
            )
        with c2:
            st.subheader("Oferta")
            df_oferta = st.data_editor(
                st.session_state.oferta,
                key="editor_oferta",
                height=300,
                use_container_width=True,
            )
        st.subheader("Demanda")
        df_demanda = st.data_editor(
            st.session_state.demanda, key="editor_demanda", use_container_width=True
        )
        c1, c2, c3 = st.columns([1, 1, 2])
        if c1.button("⬅ Menú"):
            self.transporte_navegar("Menu")
        if c2.button("🧹 Limpiar"):
            cols_names = [f"X{j+1}" for j in range(cols)]
            st.session_state.matriz_costos = pd.DataFrame(
                np.nan, index=range(filas), columns=cols_names
            )
            st.session_state.oferta = pd.DataFrame(
                0, index=range(filas), columns=["Fabricado"]
            )
            st.session_state.demanda = pd.DataFrame(
                0, index=["Demanda"], columns=cols_names
            )
            for key in ["editor_costos", "editor_oferta", "editor_demanda"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        if c3.button("Resolver 🚀", type="primary"):
            if df_oferta.values.sum() < df_demanda.values.sum():
                st.error("La Oferta debe ser mayor o igual a la Demanda.")
            else:
                st.session_state.matriz_costos = df_costos
                st.session_state.oferta = df_oferta
                st.session_state.demanda = df_demanda
                self.ejecutar_resolucion_transporte()
                self.transporte_navegar("Resolver")

    def mostrar_resolver_transporte(self):
        algo = st.session_state.algoritmo
        paso_idx = st.session_state.paso_actual
        historial = st.session_state.historial_pasos
        estado = historial[paso_idx]
        st.header(f"Resolviendo: {algo}")
        matriz_asignacion = estado["asignacion"]
        oferta_rest = estado["oferta"]
        demanda_rest = estado["demanda"]
        seleccion = estado["seleccion"]
        costos_orig = st.session_state.costos_originales_clean
        filas, cols = matriz_asignacion.shape
        cols_names = [f"X{j+1}" for j in range(cols)]
        df_visual = pd.DataFrame(matriz_asignacion, columns=cols_names).astype(str)
        for i in range(filas):
            for j in range(cols):
                val = matriz_asignacion[i, j]
                es_bloqueada = costos_orig[i, j] == np.inf
                if val > 0:
                    df_visual.iloc[i, j] = str(val)
                elif es_bloqueada:
                    df_visual.iloc[i, j] = "X"
                else:
                    df_visual.iloc[i, j] = "."
        df_visual["OFERTA"] = oferta_rest.astype(str)
        if algo == "Vogel":
            pen_filas = estado["penalizaciones"]["filas"]
            pf_str = [f"{p:.0f}" if p != -1 else "-" for p in pen_filas]
            df_visual["PEN. F"] = pf_str
        ancho_actual = df_visual.shape[1]
        fila_demanda = list(demanda_rest.astype(str))
        while len(fila_demanda) < ancho_actual:
            fila_demanda.append("")
        df_visual.loc["DEMANDA"] = fila_demanda
        if algo == "Vogel":
            pen_cols = estado["penalizaciones"]["cols"]
            pc_str = [f"{p:.0f}" if p != -1 else "-" for p in pen_cols]
            while len(pc_str) < ancho_actual:
                pc_str.append("")
            df_visual.loc["PEN. C"] = pc_str

        def aplicar_estilos(df):
            estilos = pd.DataFrame("", index=df.index, columns=df.columns)
            C_VERDE_SEL = "#90EE90"
            C_AZUL_OD = "#ADD8E6"
            C_AZUL_PEN = "#87CEEB"
            C_AMARILLO = "#FFD700"
            C_ROJO_X = "#FFCCCB"
            estilos[:] = (
                "text-align: center; vertical-align: middle; width: 60px; border: 1px solid #ddd;"
            )
            idx_filas_core = filas
            idx_cols_core = cols
            for i in range(idx_filas_core):
                for j in range(idx_cols_core):
                    if seleccion and seleccion == (i, j):
                        estilos.iloc[i, j] = (
                            f"background-color: {C_VERDE_SEL}; color: black; font-weight: bold; border: 2px solid #555;"
                        )
                    elif df.iloc[i, j] == "X":
                        estilos.iloc[i, j] = (
                            f"background-color: {C_ROJO_X}; color: #800000;"
                        )
            estilos.iloc[:idx_filas_core, idx_cols_core] = (
                f"background-color: {C_AZUL_OD}; color: black; font-weight: bold; border-left: 3px solid #444;"
            )
            estilos.iloc[idx_filas_core, :idx_cols_core] = (
                f"background-color: {C_AZUL_OD}; color: black; font-weight: bold; border-top: 3px solid #444;"
            )
            if algo == "Vogel":
                idx_pen_f = idx_cols_core + 1
                idx_pen_c = idx_filas_core + 1
                estilos.iloc[:idx_filas_core, idx_pen_f] = (
                    f"background-color: {C_AZUL_PEN}; color: black; font-weight: bold; border-left: 1px solid #999;"
                )
                estilos.iloc[idx_pen_c, :idx_cols_core] = (
                    f"background-color: {C_AZUL_PEN}; color: black; font-weight: bold; border-top: 1px solid #999;"
                )
                if seleccion:
                    sel_i, sel_j = seleccion
                    val_pen_fila = estado["penalizaciones"]["filas"][sel_i]
                    val_pen_col = estado["penalizaciones"]["cols"][sel_j]
                    if val_pen_fila >= val_pen_col:
                        estilos.iloc[sel_i, idx_pen_f] = (
                            f"background-color: {C_AMARILLO}; color: black; border: 2px solid #444;"
                        )
                    else:
                        estilos.iloc[idx_pen_c, sel_j] = (
                            f"background-color: {C_AMARILLO}; color: black; border: 2px solid #444;"
                        )
            estilos.iloc[idx_filas_core:, idx_cols_core:] = (
                "border: none; color: transparent;"
            )
            return estilos

        styler = df_visual.style.apply(aplicar_estilos, axis=None)
        st.dataframe(styler, use_container_width=True, height=500)
        st.markdown("---")
        mask = (matriz_asignacion > 0) & (costos_orig != np.inf)
        costo_total = np.sum(matriz_asignacion[mask] * costos_orig[mask])
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            st.info(f"📝 {estado['mensaje']}")
        with c2:
            st.metric("Costo Acumulado", f"$ {costo_total:,.0f}")
        with c3:
            st.metric("Paso", f"{paso_idx} / {len(historial)-1}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⬅ Menú Principal"):
                self.transporte_navegar("Menu")
        with col2:
            if st.button("✏️ Editar Datos"):
                self.transporte_navegar("Matriz")
        with col3:
            if st.button("⏪ Anterior", disabled=(paso_idx == 0)):
                st.session_state.paso_actual -= 1
                st.rerun()
        with col4:
            es_ultimo = paso_idx == len(historial) - 1
            lbl = "Finalizado ✅" if es_ultimo else "Siguiente ⏩"
            if st.button(lbl, type="primary", disabled=es_ultimo):
                st.session_state.paso_actual += 1
                st.rerun()

    # =========================================================================
    # SECCIÓN 4: GRAFICO
    # =========================================================================
    def mostrar_grapher_config(self):
        st.title("📈 Graficadora de Región Factible")
        st.info(
            "Esta herramienta grafica sistemas de 2 variables (X1, X2) con N restricciones."
        )
        num_rest = st.number_input("¿Cuántas restricciones tiene su sistema?", 1, 10, 2)

        c1, c2 = st.columns([1, 4])
        if c1.button("🏠 Inicio"):
            self.ir_a_home()
        if c2.button("Definir Funciones ➡️", type="primary"):
            st.session_state.num_rest_graph = num_rest
            st.session_state.grapher_page = 2
            st.rerun()

    def mostrar_grapher_ingreso(self):
        st.title("📝 Ingreso de Funciones")
        n = st.session_state.num_rest_graph

        with st.form("graph_form"):
            matrix_a, vector_b, ops = [], [], []
            for i in range(n):
                cols = st.columns([2, 2, 1, 2])
                with cols[0]:
                    x1 = st.number_input(f"X1", key=f"gx1_{i}", value=1.0)
                with cols[1]:
                    x2 = st.number_input(f"X2", key=f"gx2_{i}", value=1.0)
                with cols[2]:
                    op = st.selectbox("", ["<=", ">=", "="], key=f"gop_{i}")
                with cols[3]:
                    b = st.number_input(f"RHS", key=f"gb_{i}", value=10.0)
                matrix_a.append([x1, x2])
                vector_b.append(b)
                ops.append(op)

            if st.form_submit_button("Generar Gráfica 📊", type="primary"):
                st.session_state.graph_data = {
                    "A": np.array(matrix_a),
                    "b": np.array(vector_b),
                    "ops": ops,
                }
                st.session_state.grapher_page = 3
                st.rerun()
        if st.button("⬅️ Atrás"):
            st.session_state.grapher_page = 1
            st.rerun()

    def mostrar_grapher_resultado(self):

        st.title("📊 Resultado Gráfico")
        data = st.session_state.graph_data
        A, b, ops = data["A"], data["b"], data["ops"]

        # 1. Hallar intersecciones (Solo entre funciones, sin ejes)
        intersecciones = GrapherLogic.hallar_intersecciones_puras(A, b)

        # 2. Gráfica con etiquetas de coordenadas (3, 3)
        fig = go.Figure()

        max_val = np.max(b) if len(b) > 0 else 10
        limit = max_val * 1.5
        x_vals = np.linspace(0, limit, 200)

        # Dibujar líneas de restricciones
        for i in range(len(b)):
            if A[i, 1] != 0:
                y_vals = (b[i] - A[i, 0] * x_vals) / A[i, 1]
                fig.add_trace(
                    go.Scatter(x=x_vals, y=y_vals, name=f"R{i+1}", mode="lines")
                )
            else:
                x_const = b[i] / A[i, 0]
                fig.add_vline(x=x_const, line_dash="dash", annotation_text=f"R{i+1}")

        # Dibujar puntos con etiquetas de texto (X, Y)
        if intersecciones:
            px, py = zip(*intersecciones)
            fig.add_trace(
                go.Scatter(
                    x=px,
                    y=py,
                    mode="markers+text",  # Activamos marcadores y texto
                    text=[
                        f"({p[0]}, {p[1]})" for p in intersecciones
                    ],  # Generamos la etiqueta (3, 3)
                    textposition="top center",  # Posición de la etiqueta
                    marker=dict(size=10, color="black"),  # Color automático de Plotly
                    name="Intersecciones",
                )
            )

        fig.update_layout(
            xaxis_title="X1",
            yaxis_title="X2",
            xaxis_range=[0, limit],
            yaxis_range=[0, limit],
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. Tabla de Puntos (Sin colores chillones)
        st.subheader("📍 Puntos de Cruce entre Restricciones")
        if not intersecciones:
            st.warning(
                "No se encontraron cruces entre las restricciones en el primer cuadrante."
            )
        else:
            df_puntos = pd.DataFrame(
                intersecciones, columns=["Coordenada X1", "Coordenada X2"]
            )

            # Añadimos la columna de factibilidad con un diseño sobrio
            df_puntos["Estado"] = [
                (
                    "✅ Factible"
                    if GrapherLogic.es_factible(p, A, b, ops)
                    else "❌ No Factible"
                )
                for p in intersecciones
            ]

            # Mostramos la tabla con estilo minimalista
            st.dataframe(df_puntos, use_container_width=True)

        st.divider()
        if st.button("⬅️ Volver a Configuración"):
            st.session_state.grapher_page = 1
            st.rerun()

    # =========================================================================
    # SECCIÓN 5: HUNGARO
    # =========================================================================
    def mostrar_hungaro_config(self):
        st.title("🎭 Método Húngaro (Asignación)")
        st.info("El método húngaro requiere una matriz cuadrada (N x N).")
        n = st.number_input("Dimensión de la matriz (N)", 2, 15, 3)

        c1, c2 = st.columns([1, 4])
        if c1.button("🏠 Inicio"):
            self.ir_a_home()
        if c2.button("Construir Matriz 🏗️", type="primary"):
            st.session_state.hungaro_dim = n
            st.session_state.matriz_hungaro = pd.DataFrame(
                0,
                index=[f"Recurso {i+1}" for i in range(n)],
                columns=[f"Tarea {j+1}" for j in range(n)],
            )
            st.session_state.hungaro_page = 2
            st.rerun()

    def mostrar_hungaro_ingreso(self):
        st.title("📝 Ingreso de Costos de Asignación")
        df_input = st.data_editor(
            st.session_state.matriz_hungaro, use_container_width=True, height=300
        )

        c1, c2 = st.columns([1, 4])
        if c1.button("⬅️ Atrás"):
            st.session_state.hungaro_page = 1
            st.rerun()
        if c2.button("Resolver Paso a Paso 🚀", type="primary"):
            st.session_state.matriz_hungaro_orig = df_input.values.copy()
            st.session_state.hungaro_pasos = HungarianSolver.resolver(df_input.values)
            st.session_state.hungaro_paso_actual = 0
            st.session_state.hungaro_page = 3
            st.rerun()

    def mostrar_hungaro_resolver(self):
        pasos = st.session_state.hungaro_pasos
        idx = st.session_state.hungaro_paso_actual
        estado = pasos[idx]
        matriz_orig = st.session_state.matriz_hungaro_orig

        st.title("📊 Resolución Paso a Paso")
        st.info(f"💡 {estado['mensaje']}")

        # Estilizado de la matriz
        df_visual = pd.DataFrame(
            estado["matriz"],
            index=[f"R{i+1}" for i in range(len(estado["matriz"]))],
            columns=[f"T{j+1}" for j in range(len(estado["matriz"]))],
        )

        def aplicar_estilos_hungaro(df):
            estilos = pd.DataFrame("", index=df.index, columns=df.columns)
            estilos[:] = "text-align: center; vertical-align: middle;"

            # 1. Pintar Líneas (si existen en este paso)
            if estado["lineas"]:
                for r in estado["lineas"]["h"]:
                    estilos.iloc[r, :] = "background-color: #ADD8E6; color: black;"
                for c in estado["lineas"]["v"]:
                    estilos.iloc[:, c] = "background-color: #ADD8E6; color: black;"

            # 2. Pintar Asignación Final (Verde)
            if "asignacion" in estado:
                for i in range(len(df)):
                    for j in range(len(df.columns)):
                        if estado["asignacion"][i, j] == 1:
                            estilos.iloc[i, j] = (
                                "background-color: #90EE90; color: black; font-weight: bold;"
                            )
            return estilos

        st.dataframe(
            df_visual.style.apply(aplicar_estilos_hungaro, axis=None).format("{:.0f}"),
            use_container_width=True,
        )

        # Cálculo de costo si es el final
        if "asignacion" in estado:
            costo_total = np.sum(matriz_orig * estado["asignacion"])
            st.success(f"💰 Costo Total de Asignación: {costo_total}")

        # Navegación
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🏠 Inicio"):
            self.ir_a_home()
        if c2.button("✏️ Editar"):
            st.session_state.hungaro_page = 2
            st.rerun()
        if c3.button("⏪ Anterior", disabled=idx == 0):
            st.session_state.hungaro_paso_actual -= 1
            st.rerun()
        if c4.button("Siguiente ⏩", disabled=idx == len(pasos) - 1, type="primary"):
            st.session_state.hungaro_paso_actual += 1
            st.rerun()

    # =========================================================================
    # SECCIÓN 6: OPTIMIZACIÓN MODI
    # =========================================================================

    def mostrar_modi_config(self):
        st.title("🔄 Optimización MODI")
        st.markdown("### 1. Configuración de Dimensiones")
        c1, c2 = st.columns(2)
        filas = c1.number_input("Orígenes (Filas)", 2, 10, 3)
        cols = c2.number_input("Destinos (Columnas)", 2, 10, 4)
        if st.button("Crear Matriz ➡️", type="primary"):
            st.session_state.modi_costos = pd.DataFrame(
                0.0,
                index=[f"O{i+1}" for i in range(filas)],
                columns=[f"D{j+1}" for j in range(cols)],
            )
            st.session_state.modi_oferta = pd.DataFrame(
                0, index=range(filas), columns=["Oferta"]
            )
            st.session_state.modi_demanda = pd.DataFrame(
                0, index=["Demanda"], columns=[f"D{j+1}" for j in range(cols)]
            )
            st.session_state.modi_page = 2
            st.rerun()
        if st.button("🏠 Inicio"):
            self.ir_a_home()

    def mostrar_modi_ingreso(self):
        st.title("📝 2. Ingreso de Datos y Solución Inicial")
        c1, c2 = st.columns([3, 1])
        with c1:
            costos_df = st.data_editor(st.session_state.modi_costos, key="modi_c_ed")
        with c2:
            oferta_df = st.data_editor(st.session_state.modi_oferta, key="modi_o_ed")
        demanda_df = st.data_editor(st.session_state.modi_demanda, key="modi_d_ed")

        metodo = st.selectbox(
            "Método para solución inicial:",
            ["Vogel", "Costo Mínimo", "Esquina Noroeste"],
        )

        if st.button("Optimizar con MODI 🚀", type="primary"):
            c_vals = costos_df.values.astype(float)
            o_vals = oferta_df.values.flatten().astype(int)
            d_vals = demanda_df.values.flatten().astype(int)
            st.session_state.modi_costos_orig = c_vals

            # Obtener solución inicial
            if metodo == "Vogel":
                gen = Vogel.resolver(c_vals, o_vals, d_vals)
            elif metodo == "Costo Mínimo":
                gen = CostoMinimo.resolver(c_vals, o_vals, d_vals)
            else:
                gen = EsquinaNoroeste.resolver(c_vals, o_vals, d_vals)

            sol_ini = list(gen)[-1]["asignacion"]
            st.session_state.modi_pasos = ModiSolver.resolver(
                c_vals, o_vals, d_vals, sol_ini
            )
            st.session_state.modi_paso_actual = 0
            st.session_state.modi_page = 3
            st.rerun()
        if st.button("🏠 Volver al Inicio"):
            self.ir_a_home()

    def mostrar_modi_resolver(self):
        if st.session_state.modi_costos_orig is None:
            self.navegar_a("Home")
            return

        pasos = st.session_state.modi_pasos
        idx = st.session_state.modi_paso_actual
        estado = pasos[idx]
        costos_orig = st.session_state.modi_costos_orig

        st.title(f"🔄 MODI - Iteración {estado['iteracion']}")
        st.subheader(f"Sub-paso: {estado['subpaso']}")
        st.info(f"💡 {estado['mensaje']}")

        col_tab, col_eq = st.columns([2, 1])

        with col_tab:
            asignacion = estado["asignacion"]
            basicas = estado["basicas"]
            filas, cols = asignacion.shape
            df_visual = pd.DataFrame(
                "",
                index=[f"O{i+1}" for i in range(filas)],
                columns=[f"D{j+1}" for j in range(cols)],
            )

            for r in range(filas):
                for c in range(cols):
                    costo = costos_orig[r, c]
                    # Si es celda básica (está en la base)
                    if (r, c) in basicas:
                        val = (
                            f"{asignacion[r, c]:.0f}"
                            if asignacion[r, c] > 0
                            else "0 (Base)"
                        )
                        df_visual.iloc[r, c] = f"{costo:.0f} | [{val}]"
                    # Si no es básica, mostrar Delta
                    elif "deltas" in estado and estado["deltas"][r, c] is not None:
                        df_visual.iloc[r, c] = (
                            f"{costo:.0f} | (Δ:{estado['deltas'][r, c]:.0f})"
                        )
                    else:
                        df_visual.iloc[r, c] = f"{costo:.0f} | -"

            df_visual["u_i"] = [f"{x:.1f}" for x in estado["u"]]
            df_visual.loc["v_j"] = list([f"{x:.1f}" for x in estado["v"]]) + [""]

            def estilo_modi(df):
                est = pd.DataFrame("", index=df.index, columns=df.columns)
                est[:] = "text-align: center; border: 1px solid #444;"
                for r in range(filas):
                    for c in range(cols):
                        if (r, c) in basicas:
                            est.iloc[r, c] = "background-color: #90EE90; color: black;"
                        if "ciclo" in estado and (r, c) in estado["ciclo"]:
                            pos = estado["ciclo"].index((r, c))
                            color = "#FFD700" if pos % 2 == 0 else "#FF6347"
                            est.iloc[r, c] = (
                                f"background-color: {color}; color: black; font-weight: bold; border: 2px solid black;"
                            )
                        elif (
                            "deltas" in estado
                            and estado["deltas"][r, c] is not None
                            and estado["deltas"][r, c] < 0
                        ):
                            est.iloc[r, c] = "background-color: #FFCCCB; color: black;"
                est.iloc[:-1, -1] = (
                    "background-color: #ADD8E6; color: black; font-weight: bold;"
                )
                est.iloc[-1, :-1] = (
                    "background-color: #ADD8E6; color: black; font-weight: bold;"
                )
                return est

            st.dataframe(
                df_visual.style.apply(estilo_modi, axis=None), use_container_width=True
            )

            costo_total = np.sum(asignacion * costos_orig)
            st.metric("Costo Total Actual", f"$ {costo_total:,.2f}")

        with col_eq:
            st.subheader("🔢 Operaciones")
            if estado["subpaso"] == "Evaluación":
                with st.expander("1. Multiplicadores (u + v = C)", expanded=True):
                    for eq in estado.get("ecuaciones_uv", []):
                        st.caption(eq)
                with st.expander("2. Índices de Mejora (C - u - v = Δ)", expanded=True):
                    for eq in estado.get("ecuaciones_delta", []):
                        st.caption(eq)
            else:
                st.warning(f"Ajuste de Carga (θ = {estado.get('theta', 0)})")
                for i, (r, c) in enumerate(estado.get("ciclo", [])):
                    st.write(f"{'(+)' if i % 2 == 0 else '(-)'} Celda O{r+1}-D{c+1}")

        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🏠 Inicio"):
            self.ir_a_home()
        if c2.button("✏️ Editar"):
            st.session_state.modi_page = 2
            st.rerun()
        if c3.button("⏪ Anterior", disabled=idx == 0):
            st.session_state.modi_paso_actual -= 1
            st.rerun()
        if c4.button("Siguiente ⏩", disabled=idx == len(pasos) - 1, type="primary"):
            st.session_state.modi_paso_actual += 1
            st.rerun()

    # =========================================================================
    # ROUTER PRINCIPAL
    # =========================================================================
    def render(self):
        seccion = st.session_state.seccion_app

        if seccion == "Home":
            self.mostrar_home()

        elif seccion == "Simplex":
            page = st.session_state.get("simplex_page", 1)
            if page == 1:
                self.mostrar_simplex_seleccion()  # Selección de método
            elif page == 1.5:
                self.mostrar_simplex_config()  # Configuración
            elif page == 2:
                self.mostrar_simplex_ingreso()  # Matriz
            elif page == 3:
                self.mostrar_simplex_resultados()  # Tablas

        elif seccion == "Transporte":
            # Router interno de Transporte
            pagina = st.session_state.pagina
            if pagina == "Menu":
                self.mostrar_menu_transporte()
            elif pagina == "Modelo":
                self.mostrar_modelo_transporte()
            elif pagina == "Matriz":
                self.mostrar_matriz_transporte()
            elif pagina == "Resolver":
                self.mostrar_resolver_transporte()

        elif seccion == "Grapher":
            g_page = st.session_state.grapher_page
            if g_page == 1:
                self.mostrar_grapher_config()
            elif g_page == 2:
                self.mostrar_grapher_ingreso()
            elif g_page == 3:
                self.mostrar_grapher_resultado()

        elif seccion == "Hungaro":
            h_page = st.session_state.hungaro_page
            if h_page == 1:
                self.mostrar_hungaro_config()
            elif h_page == 2:
                self.mostrar_hungaro_ingreso()
            elif h_page == 3:
                self.mostrar_hungaro_resolver()

        elif seccion == "Modi":
            m_page = st.session_state.modi_page
            if m_page == 1:
                self.mostrar_modi_config()
            elif m_page == 2:
                self.mostrar_modi_ingreso()
            elif m_page == 3:
                self.mostrar_modi_resolver()
