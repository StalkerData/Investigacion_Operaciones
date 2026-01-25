import streamlit as st
import pandas as pd
import numpy as np

# --- IMPORTACIONES DE MODELOS ---
# Transporte
from Modelos.CostoMinimo import CostoMinimo
from Modelos.EsquinaNoroeste import EsquinaNoroeste
from Modelos.Vogel import Vogel
# Simplex (Tu lógica)
from Metodo.simplex_logic import SimplexSolver

class UI:
    def __init__(self):
        self.inicializar_estado()

    def inicializar_estado(self):
        # --- ESTADO GLOBAL DE NAVEGACIÓN ---
        if 'seccion_app' not in st.session_state: st.session_state.seccion_app = 'Home'
        
        # --- ESTADO TRANSPORTE ---
        if 'pagina' not in st.session_state: st.session_state.pagina = 'Menu' # Sub-navegación transporte
        if 'algoritmo' not in st.session_state: st.session_state.algoritmo = None
        if 'dimensiones' not in st.session_state: st.session_state.dimensiones = (3, 3)
        if 'matriz_costos' not in st.session_state: st.session_state.matriz_costos = pd.DataFrame()
        if 'oferta' not in st.session_state: st.session_state.oferta = pd.DataFrame()
        if 'demanda' not in st.session_state: st.session_state.demanda = pd.DataFrame()
        if 'historial_pasos' not in st.session_state: st.session_state.historial_pasos = []
        if 'paso_actual' not in st.session_state: st.session_state.paso_actual = 0
        if 'costos_originales_clean' not in st.session_state: st.session_state.costos_originales_clean = None

        # --- ESTADO SIMPLEX (Tus variables) ---
        if 'simplex_page' not in st.session_state: st.session_state['simplex_page'] = 1
        if 'num_vars' not in st.session_state: st.session_state['num_vars'] = 2
        if 'num_rest' not in st.session_state: st.session_state['num_rest'] = 2
        if 'solver_history' not in st.session_state: st.session_state['solver_history'] = None
        if 'current_step' not in st.session_state: st.session_state['current_step'] = 0

    # --- NAVEGACIÓN GLOBAL ---
    def ir_a_home(self):
        st.session_state.seccion_app = 'Home'
        st.rerun()

    def ir_a_transporte(self):
        st.session_state.seccion_app = 'Transporte'
        st.session_state.pagina = 'Menu'
        st.rerun()

    def ir_a_simplex(self):
        st.session_state.seccion_app = 'Simplex'
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
        *   **Versión:** 1.2.0 Prototipo
        *   **Tecnología:** Python + NumPy + Streamlit
        *   **Github:** [https://github.com/StalkerData](https://github.com/StalkerData)
        """)
        
        st.info("Seleccione el módulo que desea utilizar:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚚 Métodos de Transporte", type="primary", use_container_width=True):
                self.ir_a_transporte()
        with col2:
            if st.button("📐 Método Simplex", type="primary", use_container_width=True):
                self.ir_a_simplex()

    # =========================================================================
    # SECCIÓN 2: MÓDULO SIMPLEX (TU CÓDIGO INTEGRADO)
    # =========================================================================
    def simplex_navegar(self, page_num):
        st.session_state['simplex_page'] = page_num
        st.rerun()

    def mostrar_simplex_config(self):
        st.title("📐 Método Simplex - Configuración")
        st.markdown("Bienvenido. Esta herramienta te ayudará a resolver problemas de **Minimizar** paso a paso.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state['num_vars'] = st.number_input("Número de Variables (Xn)", min_value=1, max_value=10, value=st.session_state['num_vars'])
        with col2:
            st.session_state['num_rest'] = st.number_input("Número de Restricciones", min_value=1, max_value=10, value=st.session_state['num_rest'])
        
        st.write("")
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("🏠 Inicio"): self.ir_a_home()
        with c2:
            if st.button("Crear Modelo ➡️", type="primary"):
                self.simplex_navegar(2)

    def mostrar_simplex_ingreso(self):
        st.title("📝 Definición del Modelo")
        st.markdown("Ingresa los coeficientes. Si dejas un campo vacío o en 0, se tomará como nulo.")

        num_vars = st.session_state['num_vars']
        num_rest = st.session_state['num_rest']

        with st.form("simplex_form"):
            st.subheader("Función Objetivo (Max Z)")
            cols_z = st.columns(num_vars)
            coef_z = []
            for i in range(num_vars):
                with cols_z[i]:
                    val = st.number_input(f"X{i+1}", key=f"z_{i}", value=0.0)
                    coef_z.append(val)
            
            st.divider()
            st.subheader("Restricciones (Sujeto a:)")
            
            matrix_a = []
            vector_b = []

            for i in range(num_rest):
                st.markdown(f"**Restricción {i+1}**")
                cols_r = st.columns(num_vars + 2)
                row_coeffs = []
                for j in range(num_vars):
                    with cols_r[j]:
                        val = st.number_input(f"Coef X{j+1}", key=f"r_{i}_{j}", value=0.0, label_visibility="collapsed")
                        st.caption(f"X{j+1}")
                        row_coeffs.append(val)
                with cols_r[num_vars]:
                    st.markdown("### ≤")
                with cols_r[num_vars+1]:
                    rhs = st.number_input("RHS", key=f"rhs_{i}", value=0.0, label_visibility="collapsed")
                    st.caption("Límite")
                    vector_b.append(rhs)
                matrix_a.append(row_coeffs)

            st.divider()
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.form_submit_button("⬅️ Regresar"): self.simplex_navegar(1)
            with c2:
                if st.form_submit_button("Limpiar"): st.rerun()
            with c3:
                solve_clicked = st.form_submit_button("Resolver y Ver Tabla 🚀", type="primary")

        if solve_clicked:
            solver = SimplexSolver(coef_z, matrix_a, vector_b)
            history = solver.solve()
            st.session_state['solver_history'] = history
            st.session_state['current_step'] = 0
            self.simplex_navegar(3)

    def mostrar_simplex_resultados(self):
        st.title("📊 Iteraciones Simplex")
        
        history = st.session_state['solver_history']
        curr = st.session_state['current_step']
        total_steps = len(history)
        step_data = history[curr]
        
        st.progress((curr + 1) / total_steps)
        st.caption(f"Iteración {step_data['iteracion']} de {total_steps - 1} (aprox)")

        if "Solución Óptima" in step_data['mensaje']:
            st.success(f"🎉 {step_data['mensaje']}")
        else:
            st.info(f"ℹ️ {step_data['mensaje']}")

        df = step_data['df']
        
        if step_data['pivote_info']:
            fila_idx, col_idx = step_data['pivote_info']
            def highlight_pivot(x):
                style_pivote = 'background-color: #ffeb3b; color: black; font-weight: bold;'
                style_relacionado = 'background-color: #90caf9; color: black;' 
                df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
                df_styler.iloc[fila_idx, :] = style_relacionado
                df_styler.iloc[:, col_idx] = style_relacionado
                df_styler.iloc[fila_idx, col_idx] = style_pivote
                return df_styler

            st.dataframe(df.style.apply(highlight_pivot, axis=None).format("{:.2f}"), use_container_width=True)
            st.markdown(f"""
            - **Variable que Entra (Columna):** {step_data['df'].columns[col_idx]}
            - **Variable que Sale (Fila):** {step_data['df'].index[fila_idx]}
            """)
        else:
            st.dataframe(df.style.format("{:.2f}"), use_container_width=True)

        if "solucion" in step_data:
            st.divider()
            st.subheader("🏆 Resultados Finales")
            sol = step_data['solucion']
            sc1, sc2 = st.columns(2)
            with sc1: st.metric("Valor Óptimo (Z)", f"{sol['Z']:.4f}")
            with sc2:
                st.write("Variables de Decisión:")
                for k, v in sol.items():
                    if k != "Z" and not k.startswith("S"):
                        st.write(f"**{k}** = {v:.4f}")

        st.divider()
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button("🏠 Inicio App"): self.ir_a_home()
        with b2:
            if st.button("⬅️ Editar Datos"): self.simplex_navegar(2)
        with b3:
            if curr > 0:
                if st.button("⬅️ Anterior"):
                    st.session_state['current_step'] -= 1
                    st.rerun()
        with b4:
            if curr < total_steps - 1:
                if st.button("Siguiente Iteración ➡️", type="primary"):
                    st.session_state['current_step'] += 1
                    st.rerun()

    # =========================================================================
    # SECCIÓN 3: MÓDULO TRANSPORTE (CÓDIGO PREVIO)
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
        if algo == "Noroeste": generador = EsquinaNoroeste.resolver(costos, oferta, demanda)
        elif algo == "CostoMinimo": generador = CostoMinimo.resolver(costos, oferta, demanda)
        elif algo == "Vogel": generador = Vogel.resolver(costos, oferta, demanda)

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
        if st.button("🏠 Volver al Inicio"): self.ir_a_home()

    def mostrar_modelo_transporte(self):
        st.header(f"Configuración: {st.session_state.algoritmo}")
        c1, c2 = st.columns(2)
        filas = c1.number_input("Filas", 2, 20, 3)
        cols = c2.number_input("Columnas", 2, 20, 4)
        c_btn1, c_btn2 = st.columns([1, 4])
        if c_btn1.button("⬅ Menú"): self.transporte_navegar("Menu")
        if c_btn2.button("Construir Matriz 🏗️", type="primary"):
            st.session_state.dimensiones = (filas, cols)
            cols_names = [f"X{j+1}" for j in range(cols)]
            st.session_state.matriz_costos = pd.DataFrame(np.nan, index=range(filas), columns=cols_names)
            st.session_state.oferta = pd.DataFrame(0, index=range(filas), columns=["Fabricado"])
            st.session_state.demanda = pd.DataFrame(0, index=["Demanda"], columns=cols_names)
            for key in ["editor_costos", "editor_oferta", "editor_demanda"]:
                if key in st.session_state: del st.session_state[key]
            self.transporte_navegar("Matriz")

    def mostrar_matriz_transporte(self):
        st.header("Ingreso de Datos")
        filas, cols = st.session_state.dimensiones
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Costos")
            df_costos = st.data_editor(st.session_state.matriz_costos, key="editor_costos", height=300, use_container_width=True)
        with c2:
            st.subheader("Oferta")
            df_oferta = st.data_editor(st.session_state.oferta, key="editor_oferta", height=300, use_container_width=True)
        st.subheader("Demanda")
        df_demanda = st.data_editor(st.session_state.demanda, key="editor_demanda", use_container_width=True)
        c1, c2, c3 = st.columns([1, 1, 2])
        if c1.button("⬅ Menú"): self.transporte_navegar("Menu")
        if c2.button("🧹 Limpiar"):
            cols_names = [f"X{j+1}" for j in range(cols)]
            st.session_state.matriz_costos = pd.DataFrame(np.nan, index=range(filas), columns=cols_names)
            st.session_state.oferta = pd.DataFrame(0, index=range(filas), columns=["Fabricado"])
            st.session_state.demanda = pd.DataFrame(0, index=["Demanda"], columns=cols_names)
            for key in ["editor_costos", "editor_oferta", "editor_demanda"]:
                if key in st.session_state: del st.session_state[key]
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
                if val > 0: df_visual.iloc[i, j] = str(val)
                elif es_bloqueada: df_visual.iloc[i, j] = "X"
                else: df_visual.iloc[i, j] = "."
        df_visual["OFERTA"] = oferta_rest.astype(str)
        if algo == "Vogel":
            pen_filas = estado["penalizaciones"]["filas"]
            pf_str = [f"{p:.0f}" if p != -1 else "-" for p in pen_filas]
            df_visual["PEN. F"] = pf_str
        ancho_actual = df_visual.shape[1]
        fila_demanda = list(demanda_rest.astype(str))
        while len(fila_demanda) < ancho_actual: fila_demanda.append("")
        df_visual.loc["DEMANDA"] = fila_demanda
        if algo == "Vogel":
            pen_cols = estado["penalizaciones"]["cols"]
            pc_str = [f"{p:.0f}" if p != -1 else "-" for p in pen_cols]
            while len(pc_str) < ancho_actual: pc_str.append("")
            df_visual.loc["PEN. C"] = pc_str

        def aplicar_estilos(df):
            estilos = pd.DataFrame('', index=df.index, columns=df.columns)
            C_VERDE_SEL = '#90EE90'
            C_AZUL_OD   = '#ADD8E6'
            C_AZUL_PEN  = '#87CEEB'
            C_AMARILLO  = '#FFD700'
            C_ROJO_X    = '#FFCCCB'
            estilos[:] = 'text-align: center; vertical-align: middle; width: 60px; border: 1px solid #ddd;'
            idx_filas_core = filas
            idx_cols_core = cols
            for i in range(idx_filas_core):
                for j in range(idx_cols_core):
                    if seleccion and seleccion == (i, j):
                        estilos.iloc[i, j] = f'background-color: {C_VERDE_SEL}; color: black; font-weight: bold; border: 2px solid #555;'
                    elif df.iloc[i, j] == "X":
                        estilos.iloc[i, j] = f'background-color: {C_ROJO_X}; color: #800000;'
            estilos.iloc[:idx_filas_core, idx_cols_core] = f'background-color: {C_AZUL_OD}; color: black; font-weight: bold; border-left: 3px solid #444;'
            estilos.iloc[idx_filas_core, :idx_cols_core] = f'background-color: {C_AZUL_OD}; color: black; font-weight: bold; border-top: 3px solid #444;'
            if algo == "Vogel":
                idx_pen_f = idx_cols_core + 1
                idx_pen_c = idx_filas_core + 1
                estilos.iloc[:idx_filas_core, idx_pen_f] = f'background-color: {C_AZUL_PEN}; color: black; font-weight: bold; border-left: 1px solid #999;'
                estilos.iloc[idx_pen_c, :idx_cols_core] = f'background-color: {C_AZUL_PEN}; color: black; font-weight: bold; border-top: 1px solid #999;'
                if seleccion:
                    sel_i, sel_j = seleccion
                    val_pen_fila = estado["penalizaciones"]["filas"][sel_i]
                    val_pen_col = estado["penalizaciones"]["cols"][sel_j]
                    if val_pen_fila >= val_pen_col: estilos.iloc[sel_i, idx_pen_f] = f'background-color: {C_AMARILLO}; color: black; border: 2px solid #444;'
                    else: estilos.iloc[idx_pen_c, sel_j] = f'background-color: {C_AMARILLO}; color: black; border: 2px solid #444;'
            estilos.iloc[idx_filas_core:, idx_cols_core:] = 'border: none; color: transparent;'
            return estilos

        styler = df_visual.style.apply(aplicar_estilos, axis=None)
        st.dataframe(styler, use_container_width=True, height=500)
        st.markdown("---")
        mask = (matriz_asignacion > 0) & (costos_orig != np.inf)
        costo_total = np.sum(matriz_asignacion[mask] * costos_orig[mask])
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: st.info(f"📝 {estado['mensaje']}")
        with c2: st.metric("Costo Acumulado", f"$ {costo_total:,.0f}")
        with c3: st.metric("Paso", f"{paso_idx} / {len(historial)-1}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("⬅ Menú Principal"): self.transporte_navegar("Menu")
        with col2:
            if st.button("✏️ Editar Datos"): self.transporte_navegar("Matriz")
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
    # ROUTER PRINCIPAL
    # =========================================================================
    def render(self):
        seccion = st.session_state.seccion_app
        
        if seccion == 'Home':
            self.mostrar_home()
        
        elif seccion == 'Simplex':
            # Router interno de Simplex
            page = st.session_state['simplex_page']
            if page == 1: self.mostrar_simplex_config()
            elif page == 2: self.mostrar_simplex_ingreso()
            elif page == 3: self.mostrar_simplex_resultados()
            
        elif seccion == 'Transporte':
            # Router interno de Transporte
            pagina = st.session_state.pagina
            if pagina == 'Menu': self.mostrar_menu_transporte()
            elif pagina == 'Modelo': self.mostrar_modelo_transporte()
            elif pagina == 'Matriz': self.mostrar_matriz_transporte()
            elif pagina == 'Resolver': self.mostrar_resolver_transporte()