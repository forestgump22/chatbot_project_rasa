# Usa la imagen oficial de Rasa SDK, que ya tiene lo básico.
FROM rasa/rasa-sdk:3.6.2

# Establece el directorio de trabajo
WORKDIR /app

# Copia solo el código de tus acciones
COPY . .

# Instala las dependencias adicionales que necesitan tus acciones
# (principalmente para conectarse a Gemini)
RUN pip install --no-cache-dir google-generativeai python-dotenv

# El comando para iniciar el servidor de acciones. Render asignará el puerto.
CMD ["rasa", "sdk", "--actions", "actions", "-p", "$PORT", "--cors", "*"]