# Usa la imagen oficial de Rasa SDK, que ya tiene lo básico.
FROM rasa/rasa-sdk:3.6.2

# Establece el directorio de trabajo
WORKDIR /app

# --- MANEJO DE PERMISOS ---
USER root
RUN chown -R 1001:0 /opt/venv
USER 1001
# --- FIN DEL MANEJO DE PERMISOS ---

# Copia y instala los requerimientos
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# --- CAMBIO FINAL AQUÍ ---
# El comando para iniciar el servidor de acciones, usando un shell para expandir $PORT
CMD sh -c 'rasa run actions --actions actions -p $PORT --cors "*"'