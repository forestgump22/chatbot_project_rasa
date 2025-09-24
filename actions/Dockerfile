# Usa la imagen oficial de Rasa SDK
FROM rasa/rasa-sdk:3.6.2

WORKDIR /app

# Instalar dependencias específicas de Gemini
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de las acciones
COPY actions.py .

# Puerto expuesto
EXPOSE 5055

# Comando CORREGIDO - usa el formato correcto
CMD ["python", "-m", "rasa_sdk", "--actions", "actions", "--port", "5055"]