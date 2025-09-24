FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Rasa SDK específicamente
RUN pip install rasa-sdk==3.6.2

# Copiar el código de las acciones
COPY actions.py .

# Variables de entorno
ENV PORT=5055

# Exponer puerto
EXPOSE 5055

# Comando de inicio
CMD ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]