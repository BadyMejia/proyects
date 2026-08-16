FROM python:3.11-slim

# Instalar FFmpeg y librerías del sistema necesarias para audio y proceso en segundo plano
RUN apt-get update && apt-get install -y \
    ffmpeg \
    icecast2 \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copiar el requirements.txt que está dentro de python_code/
COPY python_code/requirements.txt .

# 2. Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiar todo el contenido de la carpeta python_code al directorio /app del contenedor
COPY python_code/ /app/

# Exponer los puertos (8000 para FastAPI y 8001 para Icecast si lo requieres)
EXPOSE 8000 8001

# Arrancar la aplicación principal FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
