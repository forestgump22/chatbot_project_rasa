import os 
import logging
from typing import Any, Text, Dict, List
from dotenv import load_dotenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import google.generativeai as genai

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL','gemini-pro')
        self.max_tokens = int(os.getenv('MAX_TOKENS','1000'))
        self.temperature = float(os.getenv('TEMPERATURE','0.7'))

        if not self.api_key:
            logger.error("GEMINI_API_KEY no econtrada en variables de entorno")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Gemini configurado con modelo: {self.model_name}")
        except Exception as e:
            logger.error(f"Error configurando gemini: {e}")
            self.model=None
    
    def generate_response(self, prompt:str, context: str = None) -> str:
        if not self.model:
            return "Hay problema con la configuracion de la IA."
        
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Contexto de la conversacion: {context}\n\nPregunta del usuario: {prompt}"
            
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            response = self.model.generate_content(
                full_prompt, generation_config = generation_config
            )

            return response.text
        except Exception as e:
            logger.error(f"Error generando respuesta con la IA - gemini: {e}")
            return f"Disculpa, tuve un problema con tu consulta: {str(e)}"


# Instancia global del servicio
gemini_service = GeminiService()

class ActionAskGemini(Action):
    def name(self) -> Text:
        return "accion_pregunta_gemini"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain:Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '')

        
        context = tracker.get_slot("conversacion_context") or ""
        topic = tracker.get_slot("topic")

        if topic:
            user_message = f"Sobre {topic}: {user_message}"
        
        response = gemini_service.generate_response(user_message, context)

        dispatcher.utter_message(text=response)

        new_context = f"{context}\nUsuario: {user_message}\nBot: {response}"

        return [SlotSet("conversation_context", new_context)]
    
class PeticionCreativa(Action):
    def name(self) -> Text:
        return "action_handle_creative_request"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain:Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '')

        creative_prompt = f""" 
        El usuario pidio algo creativo. Entonces se especialmente creativo y original en tu respuesta.

        Solicitud del usuario: {user_message}

        Instrucciones:
        - Si piden una historia, hazla interesante con personajes y trama
        - Si piden un poema, usea ritmo y rima apropiados
        - Si piden una lluvia de ideas, se innovador y practico.
        - Manten un tono calmado y amigable    
        """

        response = gemini_service.generate_response(creative_prompt)
        dispatcher.utter_message(text=response)

        return []
    
class ActionSetMood(Action):
    def name(self) -> Text:
        return "action_set_mood"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain:Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent', {}).get('name', '')

        if intent == "mood_great":
            mood = "happy"
            dispatcher.utter_message(text="!Me alegra saber que te sientes genial!")
        elif intent == "mood_unhappy":
            mood = "sad"
            dispatcher.utter_message(text="Entiendo que no te sientes muy bien. Hay algun en lo que te podria ayudar?")
        else:
            mood="neutral"
        
        return [SlotSet("user_mood", mood)]

class ActionProvideHelp(Action):
    def name(self)->Text:
        return "action_provide_help"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain:Dict[Text, Any]) ->List[Dict[Text, Any]]:
        help_message = """
            !Puedo ayudarte con lo que necesites! 
            ** Preguntas y explicaciones : Cualquier tema que necesites entender
            ** Programacion: Ayuda con codigo, algoritmosy debugging
            ** Creatividad: Escribir historias, poemas, lluvias de ideas
            ** Problemas tecnicos: Soluciones paso a paso
            ** Conversacion: Charlar sobre lo que quieras

        Solo preguntame lo que quieras y usare mi IA para darte la mejor respuesta posible.
        """

        dispatcher.utter_message(text=help_message)
        return []
    
class ActionDefaultFallback(Action):
    def name(self) ->Text:
        return "action_default_fallback"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_message = tracker.latest_message.get('text', '')

        fallback_prompt = f"""
        El usuario escribio: "{user_message}"

        No pude clasificar exactamente su intencion, pero como soy un asistente util, 
        profavor proporcionar una repuesta apropiada y util. Si no estas seguro dele contexto, 
        pregunta amablemente para clarificar.
        """

        response = gemini_service.generate_response(fallback_prompt)
        dispatcher.utter_message(text=response)

        return []
        

