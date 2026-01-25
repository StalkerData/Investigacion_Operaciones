# 🚛 Sistema de Optimización de Transporte & Simplex

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Status](https://img.shields.io/badge/Estado-Prototipo%20v1.2.0-orange?style=for-the-badge)

Una herramienta educativa e interactiva diseñada para resolver problemas clásicos de **Investigación de Operaciones**. Implementada con una arquitectura **MVC (Modelo-Vista-Controlador)** limpia, permite visualizar paso a paso el funcionamiento de los algoritmos de transporte y el método Simplex.

---

## 📋 Características Principales

### 1. 🚚 Módulo de Transporte
Resuelve problemas de asignación de oferta y demanda minimizando costos.
*   **Algoritmos Soportados:**
    *   📉 **Esquina Noroeste:** Método básico basado en posición.
    *   💲 **Costo Mínimo:** Prioriza las rutas más baratas.
    *   🦅 **Aproximación de Vogel:** Método avanzado basado en penalizaciones (costo de oportunidad).
*   **Visualización Avanzada:**
    *   Manejo de rutas inexistentes o bloqueadas (marcadas como `X`).
    *   Visualización asimétrica de penalizaciones en Vogel (Filas a la derecha, Columnas abajo).
    *   **Paso a Paso:** Navegación temporal (Anterior/Siguiente) para ver cómo se llena la matriz.
    *   **Feedback Visual:** Colores intuitivos (Verde para selección, Rojo para bloqueos, Azul para cabeceras).

### 2. 📐 Módulo Simplex
Resuelve problemas de programación lineal (Maximización).
*   **Capacidades:**
    *   Configuración dinámica de variables ($X_n$) y restricciones.
    *   Generación automática de variables de holgura ($S_n$).
*   **Didáctica:**
    *   Muestra la tabla Simplex en cada iteración.
    *   Resalta la **Fila Pivote**, **Columna Pivote** y el **Elemento Pivote** en amarillo/azul.
    *   Explica qué variable entra y cuál sale de la base.

---

## 🏗️ Arquitectura del Proyecto

El proyecto sigue un patrón de diseño **MVC** estricto para desacoplar la lógica matemática de la interfaz gráfica.

```text
.
├── Appy.py                  # 🎮 Controlador: Punto de entrada de la aplicación
├── dockerfile               # 🐳 Configuración para despliegue en contenedores
├── requirements.txt         # 📦 Dependencias del proyecto
├── Metodo/                  # 🧠 Lógica Simplex
│   └── simplex_logic.py     # Motor de resolución del método Simplex
├── Modelos/                 # 🧠 Lógica Transporte (Modelos Puros)
│   ├── CostoMinimo.py       # Lógica de Costo Mínimo (NumPy)
│   ├── EsquinaNoroeste.py   # Lógica de Esquina Noroeste (NumPy)
│   └── Vogel.py             # Lógica de Vogel y Penalizaciones (NumPy)
└── Pagina/                  # 🎨 Vista (Interfaz de Usuario)
    └── Paginas.py           # UI unificada con Streamlit (Renderizado y Estilos)
```

---

## 🚀 Instalación y Uso

### Opción A: Ejecución Local (Recomendado para desarrollo)

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/StalkerData/tu-repo.git
    cd tu-repo
    ```

2.  **Crear un entorno virtual (Opcional pero recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    streamlit run Appy.py
    ```

### Opción B: Docker (Recomendado para despliegue)

El proyecto está optimizado para correr en contenedores ligeros usando `python:3.13-slim`.

1.  **Construir la imagen:**
    ```bash
    docker build -t io-app .
    ```

2.  **Correr el contenedor:**
    ```bash
    docker run -p 8501:8501 io-app
    ```
    Accede a la aplicación en: `http://localhost:8501`

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso |
| :--- | :--- |
| **Python 3.13** | Lenguaje base. |
| **Streamlit** | Framework para la interfaz web interactiva. |
| **NumPy** | Cálculos matriciales de alto rendimiento para los modelos de transporte. |
| **Pandas** | Estructuración de datos y estilizado de tablas (DataFrames). |
| **Docker** | Contenización y despliegue reproducible. |

---

## 📸 Capturas de Pantalla (Conceptuales)

> *Nota: Aquí puedes agregar imágenes reales de tu aplicación.*

1.  **Menú Principal:** Selección entre Transporte y Simplex.
2.  **Matriz de Transporte:** Editor tipo Excel para ingresar costos, oferta y demanda.
3.  **Resolución Vogel:** Tabla con penalizaciones laterales e inferiores, resaltando la decisión del algoritmo.
4.  **Tabla Simplex:** Iteraciones con resaltado de pivotes.

---

## ✒️ Autor

**StalkerData**
*   Desarrollador Full Stack & Data Enthusiast.
*   [GitHub Profile](https://github.com/StalkerData)
