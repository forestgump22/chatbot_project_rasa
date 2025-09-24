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

# --- COMANDO DE INICIO EXPLÍCITO Y ROBUSTO ---
# En lugar de usar 'rasa run actions', llamamos directamente al módulo de Python
# que inicia el servidor. Esto evita problemas con los scripts de entrada del contenedor.
CMD python -m rasa_sdk --actions actions -p $PORT