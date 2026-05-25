import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# --- IMPORTACIONES DE MODELOS ---
# Transporte
from Modelos.CostoMinimo import CostoMinimo
from Modelos.EsquinaNoroeste import EsquinaNoroeste
from Modelos.Vogel import Vogel
# Simplex (Tu lógica)
from Metodo.simplex_logic import SimplexSolver
from Metodo.big_m_logic import BigMSolver
from Metodo.grapher_logic import GrapherLogic

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

        if 'grapher_page' not in st.session_state: 
            st.session_state.grapher_page = 1

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
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚚 Métodos de Transporte", type="primary", use_container_width=True):
                self.ir_a_transporte()
        with col2:
            if st.button("📐 Método Simplex", type="primary", use_container_width=True):
                self.ir_a_simplex()
        with col3:
            if st.button("📈 Graficadora Lineal", type="primary", use_container_width=True):
                st.session_state.seccion_app = 'Grapher'
                st.session_state.grapher_page = 1
                st.rerun()

    # =========================================================================
    # SECCIÓN 2: MÓDULO OPTIMIZACIÓN LINEAL (SIMPLEX & GRAN M)
    # =========================================================================
    def simplex_navegar(self, page_num):
        st.session_state['simplex_page'] = page_num
        st.rerun()

    # --- PÁGINA 1: SELECCIÓN DE MÉTODO ---
    def mostrar_simplex_seleccion(self):
        st.title("📐 Módulo de Optimización Lineal")
        st.write("Seleccione el método que desea utilizar:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Simplex Clásico")
            st.write("Para problemas estándar de **Maximización** con restricciones **≤**.")
            if st.button("Elegir Simplex Clásico", use_container_width=True):
                st.session_state.simplex_type = 'Clasico'
                st.session_state.simplex_mode = 'max'
                self.simplex_navegar(1.5) # Ir a Configuración
                
        with col2:
            st.subheader("Método de la Gran M")
            st.write("Para problemas de **Max/Min** con cualquier restricción (≤, ≥, =).")
            if st.button("Elegir Gran M", use_container_width=True):
                st.session_state.simplex_type = 'BigM'
                self.simplex_navegar(1.5) # Ir a Configuración

        if st.button("🏠 Volver al Inicio"):
            self.ir_a_home()

    # --- PÁGINA 1.5: CONFIGURACIÓN (VARS Y REST) ---
    def mostrar_simplex_config(self):
        tipo = st.session_state.get('simplex_type', 'Clasico')
        st.title(f"⚙️ Configuración: {'Simplex Clásico' if tipo == 'Clasico' else 'Gran M'}")
        
        if tipo == 'BigM':
            mode = st.radio("Objetivo del modelo:", ["Maximizar", "Minimizar"], horizontal=True)
            st.session_state['simplex_mode'] = 'max' if mode == "Maximizar" else 'min'
        else:
            st.info("El Simplex Clásico está configurado para Maximización (Estándar).")
            st.session_state['simplex_mode'] = 'max'

        col1, col2 = st.columns(2)
        with col1:
            st.session_state['num_vars'] = st.number_input("Número de Variables (Xn)", 1, 10, st.session_state.get('num_vars', 2))
        with col2:
            st.session_state['num_rest'] = st.number_input("Número de Restricciones", 1, 10, st.session_state.get('num_rest', 2))
        
        st.write("")
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("⬅️ Atrás"): self.simplex_navegar(1)
        with c2:
            if st.button("Crear Modelo ➡️", type="primary"):
                self.simplex_navegar(2)

    # --- PÁGINA 2: INGRESO DE DATOS (ADAPTATIVO) ---
    def mostrar_simplex_ingreso(self):
        tipo = st.session_state.get('simplex_type', 'Clasico')
        modo = st.session_state.get('simplex_mode', 'max')
        num_vars = st.session_state['num_vars']
        num_rest = st.session_state['num_rest']
        
        st.title(f"📝 Definición: {'Simplex Clásico' if tipo == 'Clasico' else 'Gran M'}")
        label_z = "Maximizar Z" if modo == 'max' else "Minimizar Z"

        with st.form("simplex_form"):
            st.subheader(f"Función Objetivo ({label_z})")
            cols_z = st.columns(num_vars)
            coef_z = []
            for i in range(num_vars):
                with cols_z[i]:
                    val = st.number_input(f"X{i+1}", key=f"z_{i}", value=0.0, format="%.2f")
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
                        val = st.number_input(f"Coef X{j+1}", key=f"r_{i}_{j}", value=0.0, label_visibility="collapsed", format="%.2f")
                        st.caption(f"X{j+1}"); row_coeffs.append(val)
                
                # --- LÓGICA DE OPERADOR ---
                with cols_r[num_vars]:
                    if tipo == 'Clasico':
                        st.markdown("### ≤")
                        ops.append("<=")
                    else:
                        op = st.selectbox("Op", ["<=", ">=", "="], key=f"op_{i}", label_visibility="collapsed")
                        ops.append(op)
                
                with cols_r[num_vars+1]:
                    rhs = st.number_input("RHS", key=f"rhs_{i}", value=0.0, label_visibility="collapsed", format="%.2f")
                    st.caption("Límite"); vector_b.append(rhs)
                
                matrix_a.append(row_coeffs)

            st.divider()
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.form_submit_button("⬅️ Regresar"): self.simplex_navegar(1.5)
            with c2:
                if st.form_submit_button("Limpiar"): st.rerun()
            with c3:
                solve_clicked = st.form_submit_button("Resolver y Ver Tabla 🚀", type="primary")

        if solve_clicked:
            if tipo == 'Clasico':
                from Metodo.simplex_logic import SimplexSolver
                solver = SimplexSolver(coef_z, matrix_a, vector_b)
            else:
                from Metodo.big_m_logic import BigMSolver
                solver = BigMSolver(coef_z, matrix_a, vector_b, ops, mode=modo)
            
            st.session_state['solver_history'] = solver.solve()
            st.session_state['current_step'] = 0
            self.simplex_navegar(3)

    # --- PÁGINA 3: RESULTADOS (COMÚN PARA AMBOS) ---
    def mostrar_simplex_resultados(self):
        st.title("📊 Iteraciones")
        history = st.session_state['solver_history']
        curr = st.session_state['current_step']
        total_steps = len(history)
        step_data = history[curr]
        
        st.progress((curr + 1) / total_steps)
        st.caption(f"Iteración {step_data['iteracion']} de {total_steps - 1}")

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
                    if k != "Z" and not k.startswith("S") and not k.startswith("A") and not k.startswith("E"):
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
                if st.button("Siguiente ➡️", type="primary"):
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
    # SECCIÓN 4: GRAFICO
    # =========================================================================
    def mostrar_grapher_config(self):
        st.title("📈 Graficadora de Región Factible")
        st.info("Esta herramienta grafica sistemas de 2 variables (X1, X2) con N restricciones.")
        num_rest = st.number_input("¿Cuántas restricciones tiene su sistema?", 1, 10, 2)
        
        c1, c2 = st.columns([1, 4])
        if c1.button("🏠 Inicio"): self.ir_a_home()
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
                with cols[0]: x1 = st.number_input(f"X1", key=f"gx1_{i}", value=1.0)
                with cols[1]: x2 = st.number_input(f"X2", key=f"gx2_{i}", value=1.0)
                with cols[2]: op = st.selectbox("", ["<=", ">=", "="], key=f"gop_{i}")
                with cols[3]: b = st.number_input(f"RHS", key=f"gb_{i}", value=10.0)
                matrix_a.append([x1, x2]); vector_b.append(b); ops.append(op)
            
            if st.form_submit_button("Generar Gráfica 📊", type="primary"):
                st.session_state.graph_data = {"A": np.array(matrix_a), "b": np.array(vector_b), "ops": ops}
                st.session_state.grapher_page = 3
                st.rerun()
        if st.button("⬅️ Atrás"): 
            st.session_state.grapher_page = 1
            st.rerun()

    def mostrar_grapher_resultado(self):
        st.title("📊 Resultado Gráfico")
        
        if 'graph_data' not in st.session_state:
            st.error("No hay datos para graficar.")
            if st.button("Volver"): self.ir_a_home()
            return

        data = st.session_state.graph_data
        A, b, ops = data["A"], data["b"], data["ops"]
        
        # 1. Hallar puntos
        todos_puntos = GrapherLogic.hallar_intersecciones(A, b)
        puntos_factibles = [p for p in todos_puntos if GrapherLogic.es_factible(p, A, b, ops)]
        
        # 2. Crear Gráfico
        fig = go.Figure()
        
        # Rango de visión
        limite = np.max(b) * 1.2 if len(b) > 0 and np.max(b) > 0 else 10
        x_plot = np.linspace(0, limite, 400)

        for i in range(len(b)):
            if A[i, 1] != 0: # Línea normal
                y_plot = (b[i] - A[i, 0] * x_plot) / A[i, 1]
                # Filtrar valores negativos para que el gráfico no se vea mal
                y_plot[y_plot < 0] = np.nan 
                fig.add_trace(go.Scatter(x=x_plot, y=y_plot, name=f"R{i+1}: {ops[i]} {b[i]}", mode='lines'))
            else: # Línea vertical
                x_val = b[i] / A[i, 0]
                fig.add_vline(x=x_val, line_width=2, line_dash="dash", line_color="red")

        # Dibujar vértices factibles
        if puntos_factibles:
            px, py = zip(*puntos_factibles)
            fig.add_trace(go.Scatter(
                x=px, y=py, mode='markers+text', 
                marker=dict(size=12, color='black', symbol='diamond'),
                text=[f"({x},{y})" for x,y in puntos_factibles],
                textposition="top center",
                name="Vértices Factibles"
            ))

        fig.update_layout(
            xaxis=dict(title="Variable X1", range=[0, limite]),
            yaxis=dict(title="Variable X2", range=[0, limite]),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        # 3. Tabla de Puntos
        st.subheader("📍 Análisis de Vértices")
        df_puntos = pd.DataFrame(todos_puntos, columns=["X1", "X2"])
        df_puntos["¿Es Factible?"] = [GrapherLogic.es_factible(p, A, b, ops) for p in todos_puntos]
        
        # Ordenar para que los factibles salgan primero
        df_puntos = df_puntos.sort_values(by="¿Es Factible?", ascending=False)
        
        st.dataframe(
            df_puntos.style.applymap(lambda x: 'background-color: #90EE90; color: black' if x is True else '', subset=["¿Es Factible?"]),
            use_container_width=True
        )

        if st.button("⬅️ Nueva Gráfica"):
            st.session_state.grapher_page = 1
            st.rerun()


    # =========================================================================
    # ROUTER PRINCIPAL
    # =========================================================================
    def render(self):
        seccion = st.session_state.seccion_app
        
        if seccion == 'Home':
            self.mostrar_home()
        
        elif seccion == 'Simplex':
            page = st.session_state.get('simplex_page', 1)
            if page == 1: self.mostrar_simplex_seleccion()   # Selección de método
            elif page == 1.5: self.mostrar_simplex_config()   # Configuración
            elif page == 2: self.mostrar_simplex_ingreso()    # Matriz
            elif page == 3: self.mostrar_simplex_resultados() # Tablas
            
        elif seccion == 'Transporte':
            # Router interno de Transporte
            pagina = st.session_state.pagina
            if pagina == 'Menu': self.mostrar_menu_transporte()
            elif pagina == 'Modelo': self.mostrar_modelo_transporte()
            elif pagina == 'Matriz': self.mostrar_matriz_transporte()
            elif pagina == 'Resolver': self.mostrar_resolver_transporte()

        elif seccion == 'Grapher':
            g_page = st.session_state.grapher_page
            if g_page == 1: self.mostrar_grapher_config()
            elif g_page == 2: self.mostrar_grapher_ingreso()
            elif g_page == 3: self.mostrar_grapher_resultado()