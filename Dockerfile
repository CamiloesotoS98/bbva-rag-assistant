# Usa una imagen oficial y ligera de Python 3.12
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para SQLite y compilaciones básicas
RUN apt-get update && apt-get install -y build-essential sqlite3

# Copia los archivos de requerimientos e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código fuente y datos al contenedor
COPY . .

# Expone el puerto que usa Streamlit
EXPOSE 8501

# Comando por defecto para levantar la interfaz de Streamlit
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.address=0.0.0.0"]