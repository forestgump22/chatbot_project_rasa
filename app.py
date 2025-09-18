from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')

#Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RASA_API_URL = ''

class RasaService:
    @staticmethod
    def send_message(message:str, sender_id:str = "user"):
        """Envia mensaje a Rasa y obtiene respuesta"""
        try:
            payload = {
                "sender": sender_id,
                "message": message
            }

            response = request.post(RASA_API_URL, json = payload, timeout=10)
            response.raise_for_status()

            rasa_reponses = response.json()

            if rasa_reponses: 
                # Combinacion de todas las respuestas de Rasa
                combined_response = "\n".join([resp.get("text","") for resp in rasa_reponses if resp.get("text")])
                return {
                    "response": combined_response,
                    "source": "rasa",
                    "raw_responses": rasa_reponses
                }
            else:
                return {
                    "response": "No pude procesar tu mensaje. Podrias intentar de nuevo?",
                    "source": "fallback",
                    "error": "Ninguna respuesta de Rasa"
                }
        except request.exceptions.RequestException as e:
            logger.error(f"Error conectando con Rasa: {e}")
            return {
                "response": "Lo siento, hay un problema de conexion. Asegurate de que Rasa este ejecutandose.",
                "source": "error",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error procesando respuesta de Rasa: {e}")
            return {
                "response": "Ocurrio un error inesperado. Por favor, intenta de nuevo.",
                "source": "error",
                "error": str(e)
            }
        
@app.route('/')
def home():
    return render_template('index.html')

@app.route()

