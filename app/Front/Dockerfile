# Usar una imagen base de Python
FROM python:3.9-slim

# Instalar las dependencias necesarias
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del frontend
COPY . .

# Exponer el puerto en el que corre Flet
EXPOSE 8500

# Comando para ejecutar la aplicación
CMD ["flet", "mainfront.py", "--port", "8500", "--host", "0.0.0.0"]