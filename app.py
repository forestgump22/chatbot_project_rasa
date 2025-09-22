from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app) # Habilita CORS para permitir peticiones desde el frontend
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-dev')

# Configurar logging para ver lo que sucede
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL del servidor de RASA. Asegúrate de que RASA esté corriendo.
# Por defecto, RASA corre en el puerto 5005.
RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route('/')
def home():
    """Sirve la página principal del chat."""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Este endpoint recibe los mensajes del usuario desde el frontend,
    los envía a RASA y devuelve la respuesta de RASA al frontend.
    """
    try:
        user_message = request.json['message']
        sender_id = request.json.get('sender', 'user') # Usar un ID de sesión si está disponible

        logger.info(f"Mensaje recibido de '{sender_id}': {user_message}")

        # Payload para enviar a RASA
        payload = {
            "sender": sender_id,
            "message": user_message
        }

        # Enviar el mensaje a RASA
        rasa_response = requests.post(RASA_API_URL, json=payload)
        rasa_response.raise_for_status() # Lanza un error si la petición a RASA falla

        rasa_messages = rasa_response.json()
        logger.info(f"Respuesta de RASA: {rasa_messages}")
        
        # Devolver la respuesta de RASA al frontend
        return jsonify(rasa_messages)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servidor de RASA: {e}")
        return jsonify([{"text": "Lo siento, no puedo conectarme con el asistente en este momento. Por favor, inténtalo más tarde."}]), 503
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado en el webhook: {e}")
        return jsonify([{"text": "Ha ocurrido un error inesperado. Por favor, intenta de nuevo."}]), 500

if __name__ == '__main__':
    # Corre la aplicación Flask en el puerto 5000
    app.run(debug=True, port=5000)