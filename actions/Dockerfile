# Usa la imagen oficial de Rasa SDK como base, que ya tiene Python y rasa-sdk.
FROM rasa/rasa-sdk:3.6.2

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu servidor de acciones al contenedor
# Copiamos requirements.txt primero para aprovechar el caché de Docker
COPY ./requirements.txt .

# Instala las dependencias adicionales que necesitan tus acciones (como google-generativeai)
# --no-cache-dir reduce el tamaño de la imagen final
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de las acciones
COPY . .

# Expone el puerto que el servidor de acciones usará
EXPOSE 5055

# El comando por defecto para iniciar el servidor de acciones cuando el contenedor se inicie
CMD ["rasa", "sdk", "--actions", "actions", "-p", "5055", "--cors", "*"]