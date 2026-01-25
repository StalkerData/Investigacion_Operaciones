import streamlit as st
import sys
import os

# Agregamos el directorio actual al path para que Python encuentre los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

##from Pagina.Paginas import UI
from Paginas.Paginas import UI
# Configuración global de la página (debe ser la primera instrucción de Streamlit)
st.set_page_config(
    page_title="Prototipo IO - Transporte & Simplex",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Instanciamos la Interfaz de Usuario
    app = UI()
    # Renderizamos la vista actual
    app.render()

if __name__ == "__main__":
    main()
