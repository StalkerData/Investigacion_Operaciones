# 🚛 Optimizador Integral de Investigación de Operaciones (IO)

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Status](https://img.shields.io/badge/Estado-Estable%20v2.0.0-green?style=for-the-badge)

Una plataforma educativa avanzada diseñada para resolver y visualizar paso a paso los algoritmos más críticos de la **Investigación de Operaciones**. Construida bajo una arquitectura **MVC** robusta, esta herramienta permite a estudiantes y profesionales entender la lógica matemática detrás de la optimización.

---

## 📋 Módulos y Características

### 1. 🚚 Modelos de Transporte
Soluciones iniciales para problemas de distribución.
*   **Algoritmos:** Esquina Noroeste, Costo Mínimo y Aproximación de Vogel.
*   **Visualización:** Mega-matriz integrada con Oferta y Demanda.
*   **Robustez:** Manejo automático de rutas inexistentes (`X`) y problemas degenerados.

### 2. 📐 Optimización Lineal (Simplex & Gran M)
Resolución de problemas de programación lineal con N variables.
*   **Simplex Clásico:** Especializado en maximización estándar con restricciones `≤`.
*   **Método de la Gran M:** Soporte completo para **Maximización y Minimización** con restricciones `≤`, `≥` e `=`.
*   **Didáctica:** Resaltado dinámico de fila/columna pivote y variables que entran/salen de la base.

### 3. 🔄 Optimización de Transporte (MODI)
El motor de optimización más avanzado de la suite.
*   **Optimización Real:** No solo evalúa, sino que ejecuta la **redistribución de carga** mediante la detección de ciclos (loops).
*   **Transparencia Matemática:** Desglose completo de ecuaciones para multiplicadores ($u_i, v_j$) e índices de mejora ($\Delta_{ij}$).
*   **Manejo de Degeneración:** Uso de $\epsilon$ (épsilon) para resolver sistemas de ecuaciones en bases incompletas.

### 4. 🎭 Método Húngaro (Asignación)
Optimización de tareas y recursos.
*   **Visualización:** Proceso de reducción de ceros y trazado de líneas mínimas.
*   **Resultado:** Resaltado de la asignación óptima y cálculo automático del costo total.

### 5. 📈 Graficadora Lineal 2D
Visualización geométrica de la optimización.
*   **Región Factible:** Renderizado dinámico de inecuaciones usando **Plotly**.
*   **Análisis de Vértices:** Identificación automática de puntos de intersección y validación de factibilidad (✅/❌).

---

## 🏗️ Arquitectura del Proyecto (MVC)

El proyecto separa estrictamente la lógica de cálculo de la interfaz de usuario:

```text
.
├── Appy.py                  # 🎮 Controlador Principal
├── dockerfile               # 🐳 Configuración de Contenedor (Debian-slim)
├── requirements.txt         # 📦 Dependencias (Versiones fijas)
├── Metodo/                  # 🧠 Motores de Optimización
│   ├── big_m_logic.py       # Lógica Gran M
│   ├── grapher_logic.py     # Álgebra de intersecciones
│   ├── hungarian_logic.py   # Algoritmo Húngaro
│   ├── modi_logic.py        # Optimizador MODI (Ciclos y Dualidad)
│   └── simplex_logic.py     # Simplex Estándar
├── Modelos/                 # 🧠 Modelos de Transporte (Generadores)
│   ├── CostoMinimo.py
│   ├── EsquinaNoroeste.py
│   └── Vogel.py
└── Pagina/                  # 🎨 Vista (Streamlit)
    └── Paginas.py           # UI Unificada y Estilos Dinámicos
```

---

## 🚀 Instalación y Despliegue

### Local
```bash
git clone https://github.com/StalkerData/investigacion_operaciones.git
pip install -r requirements.txt
streamlit run Appy.py
```

### Docker
```bash
docker build -t io-suite .
docker run -p 8501:8501 io-suite
```

---

## 🛠️ Tecnologías
*   **Python 3.13**: Core del sistema.
*   **NumPy**: Procesamiento matricial de alto rendimiento.
*   **Pandas**: Gestión de datos y estilizado de tablas.
*   **Plotly**: Gráficos interactivos.
*   **Streamlit**: Interfaz web reactiva.

---

## ✒️ Autor
**StalkerData**
*   [GitHub](https://github.com/StalkerData)
*   Proyecto desarrollado con enfoque en la enseñanza de la Investigación de Operaciones.