# --- Etapa 1: Builder (La cocina) ---
FROM python:3.13-slim AS builder

# Evitar archivos .pyc y habilitar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Instalamos herramientas de compilación solo si son necesarias
# (Muchos paquetes de Python 3.13 aún podrían requerir compilar wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Creamos un entorno virtual para aislar las dependencias
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- Etapa 2: Runtime (El plato final) ---
FROM python:3.13-slim AS runtime

# Variables de entorno de ejecución
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Instalamos SOLO lo necesario para correr (curl para el healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el entorno virtual desde la etapa builder
# Esto trae todas las librerías ya instaladas, sin la basura del compilador
COPY --from=builder /opt/venv /opt/venv

# Seguridad: Usuario no-root
RUN useradd -m -u 1000 streamlituser
USER streamlituser

# Copiamos el código de la aplicación con los permisos correctos
COPY --chown=streamlituser:streamlituser . .

# Exponer puerto
EXPOSE 8501

# Healthcheck profesional
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Ejecución
CMD ["streamlit", "run", "Appy.py", "--server.port=8501", "--server.address=0.0.0.0"]