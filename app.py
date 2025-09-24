from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
from dotenv import load_dotenv
import json
import time
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-dev')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN ---
RASA_API_URL = os.getenv("RASA_API_URL", "https://chatbot-rasa.onrender.com/webhooks/rest/webhook")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configuración de Gemini con manejo de errores
try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        logger.info("Modelo Gemini cargado exitosamente.")
    else:
        gemini_model = None
        logger.warning("GEMINI_API_KEY no encontrada. El modo NLU de Gemini no estará disponible.")
except Exception as e:
    gemini_model = None
    logger.error(f"Error al configurar Gemini: {e}. El modo NLU de Gemini no estará disponible.")

# --- PLANTILLA PARA NLU CON GEMINI (PROMPT ENGINEERING) ---
INTENT_PROMPT_TEMPLATE = """
Eres un motor de Comprensión de Lenguaje Natural (NLU) altamente preciso. Tu tarea es analizar el texto del usuario y extraer su intención y entidades en formato JSON.

REGLAS CRÍTICAS:
1.  **PRIORIDAD MÁXIMA:** Si el texto del usuario indica una emergencia médica, una situación de vida o muerte, o menciona síntomas graves como "infarto", "derrame cerebral", "no puedo respirar", etc., DEBES clasificar la intención como "contacto_emergencia", sin importar qué más diga.
2.  El JSON de salida DEBE tener una clave "intent" y una clave "entities".
3.  La clave "intent" DEBE ser uno de los siguientes valores: {intents_list}.
4.  La clave "entities" DEBE ser una lista de objetos JSON, cada uno con una clave "entity" y una clave "value".
5.  Las entidades posibles son: {entities_list}.
6.  Si después de aplicar la regla de emergencia, no puedes identificar una intención de la lista con confianza, asigna el intent "nlu_fallback".
7.  Si no encuentras entidades, devuelve una lista vacía [].
8.  Tu respuesta DEBE contener únicamente el objeto JSON y nada más.

### EJEMPLO DE PRIORIDAD MÁXIMA
Texto: "me duele el pecho y creo que estoy teniendo un infarto"
JSON: {{"intent": "contacto_emergencia", "entities": []}}

### TAREA
Texto del usuario: "{user_message}"
JSON:
"""

# Definición centralizada de intenciones y entidades conocidas por el sistema RASA
VALID_INTENTS = [
    "greet", "goodbye", "affirm", "deny", "ask_help", "switch_domain",
    "consultar_producto", "verificar_stock", "estado_pedido", "recomendar_producto", "finalizar_compra", "pagar_pedido",
    "consultar_saldo", "realizar_transferencia", "bloquear_tarjeta", "asesor_financiero",
    "agendar_cita", "consultar_sintoma", "informacion_medicamento", "contacto_emergencia",
    "pregunta_abierta", "nlu_fallback"
]
VALID_ENTITIES = [
    "producto", "numero_pedido", "categoria", "interes", "tipo_cuenta", "cantidad",
    "cuenta_destino", "tipo_tarjeta", "especialidad", "fecha_hora", "sintoma", "medicamento", "dominio"
]


def get_intent_from_gemini_robust(user_message, max_retries=2):
    """
    Función robusta para obtener la intención de Gemini, con reintentos y validación de JSON.
    """
    if not gemini_model:
        logger.error("Se intentó usar el NLU de Gemini, pero el modelo no está disponible.")
        return None

    prompt = INTENT_PROMPT_TEMPLATE.format(
        intents_list=json.dumps(VALID_INTENTS),
        entities_list=json.dumps(VALID_ENTITIES),
        user_message=user_message
    )
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Intento {attempt + 1} de NLU con Gemini.")
            response = gemini_model.generate_content(prompt)
            
            # Limpiar la respuesta para extraer solo el JSON
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            
            # Validar el JSON
            parsed_json = json.loads(cleaned_response)
            
            # Validar la estructura del JSON
            if "intent" in parsed_json and "entities" in parsed_json and isinstance(parsed_json["entities"], list):
                logger.info(f"NLU de Gemini exitoso: {parsed_json}")
                return parsed_json
            else:
                logger.warning(f"Respuesta de Gemini no tiene la estructura esperada: {cleaned_response}")

        except json.JSONDecodeError:
            logger.warning(f"Respuesta de Gemini no es un JSON válido: {response.text}")
        except Exception as e:
            logger.error(f"Error inesperado en la llamada a Gemini: {e}")
        
        # Esperar un poco antes de reintentar
        time.sleep(0.5)

    logger.error(f"Fallaron todos los intentos de obtener NLU de Gemini para el mensaje: '{user_message}'")
    return None # Devolver None si todos los intentos fallan


def get_rasa_response(sender_id, message):
    """
    Función para enviar un mensaje a RASA y obtener la respuesta.
    """
    payload = {"sender": sender_id, "message": message}
    try:
        response = requests.post(RASA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de conexión con el servidor de RASA: {e}")
        return [{"text": "Lo siento, no puedo conectarme con el asistente en este momento."}]
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado al comunicarse con RASA: {e}")
        return [{"text": "Ha ocurrido un error inesperado."}]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_message = data['message']
    sender_id = data.get('sender', 'user')
    # Extraer el modo NLU de los metadatos, con 'rasa' como valor por defecto
    nlu_mode = data.get('metadata', {}).get('nlu_mode', 'rasa')

    logger.info(f"Mensaje: '{user_message}', Sender: '{sender_id}', Modo NLU: '{nlu_mode}'")

    if nlu_mode == 'gemini':
        nlu_data = get_intent_from_gemini_robust(user_message)
        
        # Si Gemini falla, cambiamos al modo RASA como fallback para esta petición
        if nlu_data is None:
            logger.warning("Fallback a NLU de RASA debido a un error de Gemini.")
            rasa_messages = get_rasa_response(sender_id, user_message)
            # Añadir un mensaje para informar al usuario del cambio
            rasa_messages.insert(0, {"text": "(Hubo un problema con el modo inteligente, usando el modo rápido para esta respuesta.)"})
            return jsonify(rasa_messages)

        # Si Gemini tiene éxito, construimos el mensaje para RASA Core
        intent_name = nlu_data.get("intent", "nlu_fallback")
        entities = nlu_data.get("entities", [])
        
        if entities:
            entity_payload = json.dumps({entity['entity']: entity['value'] for entity in entities if 'entity' in entity and 'value' in entity})
            rasa_message = f"/{intent_name}{entity_payload}"
        else:
            rasa_message = f"/{intent_name}"
        
        logger.info(f"Inyectando a RASA Core: {rasa_message}")
        rasa_messages = get_rasa_response(sender_id, rasa_message)

    else: # nlu_mode == 'rasa'
        logger.info("Usando NLU de RASA.")
        rasa_messages = get_rasa_response(sender_id, user_message)
        
    return jsonify(rasa_messages)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)