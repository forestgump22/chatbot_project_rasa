# Usa la imagen oficial de Rasa SDK
FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

# Cambiar a root temporalmente para instalar dependencias
USER root

# Instalar dependencias específicas de Gemini
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Volver al usuario no-root para seguridad
USER 1001

# Copiar el código de las acciones
COPY actions.py .

# Puerto expuesto
EXPOSE 5055

# Comando de inicio CORREGIDO
CMD ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]