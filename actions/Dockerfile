# Usa la imagen oficial de Rasa SDK, que ya tiene lo básico.
FROM rasa/rasa-sdk:3.6.2

# Establece el directorio de trabajo
WORKDIR /app

# --- MANEJO DE PERMISOS ---
# Cambia temporalmente al usuario ROOT para poder modificar permisos.
USER root
# Cambia el dueño del directorio del entorno virtual al usuario 'rasa' (UID 1001).
RUN chown -R 1001:0 /opt/venv
# Vuelve al usuario sin privilegios para todas las operaciones posteriores.
USER 1001
# --- FIN DEL MANEJO DE PERMISOS ---

# Copia el archivo de requerimientos PRIMERO.
# Esto aprovecha el caché de Docker. Si no cambias los requerimientos,
# Docker no volverá a ejecutar pip install, haciendo los builds más rápidos.
COPY ./requirements.txt .

# Instala las dependencias desde el archivo de requerimientos.
RUN pip install --no-cache-dir -r requirements.txt

# Ahora, copia el resto del código de tus acciones (actions.py, etc.)
COPY . .

# El comando para iniciar el servidor de acciones. Render asignará el puerto.
CMD ["rasa", "sdk", "--actions", "actions", "-p", "$PORT", "--cors", "*"]