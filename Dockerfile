FROM python:3.11-slim

# Crear carpeta dentro del contenedor
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la API al contenedor
COPY api.py .

# Puerto que expone Flask
EXPOSE 5000

# Comando por defecto
CMD ["python", "api.py"]
