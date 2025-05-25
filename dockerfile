# Imagen base
FROM python:3.11-slim

# Instala dependencias del sistema necesarias para reportlab y otras bibliotecas
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Variables de entorno
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Exponer el puerto
EXPOSE 5000

# Ejecutar Gunicorn con Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
