import os
import logging
from typing import Any, Text, Dict, List
from dotenv import load_dotenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction # Importar FollowupAction

import google.generativeai as genai

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SERVICIO DE IA GENERATIVA ---
class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY no encontrada en variables de entorno. Las respuestas de IA generativa no funcionarán.")
            self.model = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Servicio Gemini configurado con el modelo: {self.model_name}")
        except Exception as e:
            logger.error(f"Error configurando Gemini: {e}. Las respuestas de IA generativa no funcionarán.")
            self.model = None
    
    def generate_response(self, prompt: str, domain: str = "general") -> str:
        if not self.model:
            return "Lo siento, hay un problema con la configuración de la IA en este momento."
        
        # Adaptar el prompt según el dominio
        system_prompt = ""
        if domain == "ecommerce":
            system_prompt = "Eres un asistente experto para una tienda online de tecnología. Responde de forma clara y útil sobre productos, stock o pedidos. Siempre mantén un tono comercial pero amigable."
        elif domain == "banca":
            system_prompt = "Eres un asistente bancario. Responde con precisión sobre saldos, transferencias, bloqueos de tarjeta o asesoramiento financiero. Prioriza la seguridad y la claridad en la información."
        elif domain == "salud":
            system_prompt = "Eres un asistente de salud. Proporciona información general sobre síntomas, citas o medicamentos. NO eres un médico, no hagas diagnósticos ni prescribas tratamientos. Siempre recomienda consultar a un profesional de la salud en caso de emergencia o dudas médicas."
        else: # general o fallback
            system_prompt = "Eres un asistente general y útil."

        full_prompt = f"{system_prompt}\n\nPregunta del usuario: \"{prompt}\""

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generando respuesta con Gemini: {e}")
            return f"Disculpa, tuve un problema al procesar tu consulta con la IA: {str(e)}"

# Instancia global del servicio para reutilizarla
gemini_service = GeminiService()

# --- ACCIONES GENERALES ---

class ActionSetDomain(Action):
    def name(self) -> Text:
        return "action_set_domain"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Este slot ya se mapea automáticamente desde el domain.yml si hay una entidad 'dominio'
        # o un intent que lo active. Esta acción es más para confirmación o lógica adicional.
        current_domain = tracker.get_slot("current_domain")
        
        if current_domain == "ecommerce":
            dispatcher.utter_message(text="¡Perfecto! Estamos en el dominio de e-commerce. ¿Cómo puedo ayudarte con tus compras o pedidos?")
        elif current_domain == "banca":
            dispatcher.utter_message(text="Entendido, pasamos al dominio de banca. ¿Qué operación o consulta bancaria tienes?")
        elif current_domain == "salud":
            dispatcher.utter_message(text="Ahora estamos en el dominio de salud. Recuerda que solo puedo dar información general y no soy un sustituto de un profesional médico. ¿En qué te puedo asistir?")
        else:
            dispatcher.utter_message(text="No estoy seguro de qué dominio quieres hablar. ¿Podrías ser más específico (e-commerce, banca, salud)?")
        
        return []

class ActionProvideHelp(Action):
    def name(self) -> Text:
        return "action_provide_help"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        help_message = """
        ¡Claro! Puedo ayudarte con varias cosas en estos dominios:
        
        **E-commerce (Compras online):**
        - Consultar productos: "Háblame del iPhone 15"
        - Verificar stock: "¿Hay stock de la RTX 4080?"
        - Estado de tu pedido: "Rastrear mi pedido 123-ABC-789"
        - Recomendaciones: "Recomiéndame una laptop para estudios"
        
        **Banca (Servicios financieros):**
        - Consultar saldo: "¿Cuál es mi saldo de ahorros?"
        - Realizar transferencias: "Quiero transferir 500 a la cuenta 123456"
        - Bloquear tarjeta: "Bloquear mi tarjeta de crédito"
        
        **Salud (Información y citas):**
        - Agendar citas: "Agendar cita con un dentista"
        - Consultar síntomas: "Tengo fiebre y tos"
        - Información de medicamentos: "Información sobre ibuprofeno"
        
        También puedo responder preguntas generales. Solo dime qué necesitas.
        """
        dispatcher.utter_message(text=help_message)
        return []

class ActionAskGemini(Action):
    def name(self) -> Text:
        return "accion_pregunta_gemini"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text', '')
        current_domain = tracker.get_slot("current_domain") or "general"
        
        # El prompt se adapta dentro del servicio Gemini
        response = gemini_service.generate_response(user_message, domain=current_domain)
        dispatcher.utter_message(text=response)
        return []

# ======================================================================================================
# --- E-COMMERCE: ACCIONES PARA TIENDA ONLINE ---
# ======================================================================================================

class ActionVerificarStock(Action):
    def name(self) -> Text:
        return "action_verificar_stock"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        producto = tracker.get_slot("producto")
        if not producto:
            dispatcher.utter_message(text="Claro, ¿qué producto te gustaría consultar?")
            return []

        # --- SIMULACIÓN DE CONSULTA A BASE DE DATOS/API DE INVENTARIO ---
        # En un entorno real, aquí se haría una llamada a una API de tu sistema de inventario.
        stock_db = {
            "iphone 15": 50,
            "samsung galaxy s24": 35,
            "rtx 4080": 0,
            "teclado mecánico keychron": 120,
            "monitor ultrawide": 15,
            "auriculares bluetooth": 200
        }
        
        stock_disponible = stock_db.get(producto.lower(), 0)
        
        if stock_disponible > 0:
            message = f"¡Buenas noticias! Tenemos {stock_disponible} unidades de {producto} en stock."
        else:
            message = f"Lo siento, actualmente no tenemos stock de {producto}. ¿Te gustaría que te notifique cuando vuelva a estar disponible?"
        
        dispatcher.utter_message(text=message)
        return []

class ActionConsultarEstadoPedido(Action):
    def name(self) -> Text:
        return "action_consultar_estado_pedido"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        num_pedido = tracker.get_slot("numero_pedido")
        if not num_pedido:
            dispatcher.utter_message(text="Claro, por favor, indícame tu número de pedido.")
            return []

        # --- SIMULACIÓN DE CONSULTA A API DE LOGÍSTICA/CRM ---
        # Aquí se integraría con un sistema de gestión de pedidos real.
        pedidos_db = {
            "123-abc-789": "Enviado. Se espera que llegue en 2 días hábiles.",
            "xyz-987-654": "Procesando. Tu pedido está siendo preparado en nuestro almacén.",
            "ord-001": "Retrasado. Lamentamos el inconveniente, la nueva fecha estimada es el 15 de Octubre.",
            "ord-456-111": "Entregado. ¡Esperamos que lo disfrutes!"
        }
        
        estado = pedidos_db.get(num_pedido.lower(), "No pudimos encontrar un pedido con ese número. Por favor, verifica que sea correcto.")
        
        dispatcher.utter_message(text=f"El estado de tu pedido {num_pedido} es: {estado}")
        return []

class ActionRecomendarProducto(Action):
    def name(self) -> Text:
        return "action_recomendar_producto"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        categoria = tracker.get_slot("categoria")
        interes = tracker.get_slot("interes")

        # --- Lógica de Recomendación (simple o basada en LLM) ---
        # Esto podría ser una búsqueda en una base de datos de productos
        # o un prompt a Gemini para generar una recomendación inteligente.
        
        if not categoria and not interes:
            dispatcher.utter_message(text="Para recomendarte un producto, ¿qué tipo de producto te interesa y para qué uso lo necesitas?")
            return []
        
        prompt_recommendation = f"El usuario busca una recomendación de {categoria or 'producto'} para {interes or 'uso general'}. Como experto en ventas, sugiere 2-3 productos populares de tu tienda y explica brevemente por qué son buenas opciones."
        
        recommendation = gemini_service.generate_response(prompt_recommendation, domain="ecommerce")
        dispatcher.utter_message(text=f"Aquí tienes algunas recomendaciones:\n{recommendation}")

        return [SlotSet("categoria", None), SlotSet("interes", None)] # Limpiar slots para futuras recomendaciones

class ActionFinalizarCompra(Action):
    def name(self) -> Text:
        return "action_finalizar_compra"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # --- SIMULACIÓN: RECUPERAR CARRITO DE COMPRAS ---
        # En una aplicación real, aquí se integraría con el sistema de carrito de compras del usuario.
        cart_items = ["iPhone 15", "Auriculares Bluetooth"] # Ejemplo
        total_price = 1299.99 # Ejemplo

        if not cart_items:
            dispatcher.utter_message(text="Tu carrito de compras está vacío. ¿Te gustaría explorar nuestros productos?")
            return []

        cart_summary = ", ".join(cart_items)
        dispatcher.utter_message(text=f"Tu carrito contiene: {cart_summary}. El total es ${total_price:.2f}. ¿Deseas confirmar la compra?")
        # RASA esperará un 'affirm' o 'deny' después de esto, por la story.yml
        return [SlotSet("total_price", total_price)] # Guardar para la acción de pago

class ActionPagarPedido(Action):
    def name(self) -> Text:
        return "action_pagar_pedido"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        total_price = tracker.get_slot("total_price")

        if not total_price:
            dispatcher.utter_message(text="Parece que no hay un pedido activo para pagar. ¿Te gustaría iniciar una compra?")
            return []
        
        # --- SIMULACIÓN DE PROCESO DE PAGO ---
        # Aquí se integraría con una pasarela de pago (Stripe, PayPal, etc.).
        # Se pedirían detalles de pago o se redirigiría al usuario.
        dispatcher.utter_message(text=f"Procediendo al pago de ${total_price:.2f}. Te enviaremos un enlace seguro para completar la transacción. ¡Gracias por tu compra!")
        
        return [SlotSet("total_price", None)] # Limpiar slot después de pagar

# ======================================================================================================
# --- BANCA: ACCIONES PARA SERVICIOS FINANCIEROS ---
# ======================================================================================================

class ActionConsultarSaldo(Action):
    def name(self) -> Text:
        return "action_consultar_saldo"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tipo_cuenta = tracker.get_slot("tipo_cuenta")
        
        # --- SIMULACIÓN DE CONSULTA A SISTEMA BANCARIO ---
        # Aquí se integrarían con APIs bancarias (OAuth2, PSD2, etc.).
        # Requiere autenticación del usuario.
        
        if not tipo_cuenta:
            dispatcher.utter_message(text="¿De qué tipo de cuenta te gustaría consultar el saldo (ej: ahorros, corriente, inversiones)?")
            return []
        
        # Simulación de saldos
        saldos_db = {
            "ahorros": 1500.75,
            "corriente": 800.50,
            "inversiones": 5000.00
        }
        
        saldo = saldos_db.get(tipo_cuenta.lower(), None)

        if saldo is not None:
            dispatcher.utter_message(text=f"Tu saldo en la cuenta de {tipo_cuenta} es: ${saldo:.2f}")
        else:
            dispatcher.utter_message(text=f"No pude encontrar información para el tipo de cuenta '{tipo_cuenta}'. Por favor, verifica el tipo de cuenta.")
        
        return [SlotSet("tipo_cuenta", None)]

class ActionRealizarTransferencia(Action):
    def name(self) -> Text:
        return "action_realizar_transferencia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        cantidad = tracker.get_slot("cantidad")
        cuenta_destino = tracker.get_slot("cuenta_destino")

        if not cantidad or not cuenta_destino:
            dispatcher.utter_message(text="Para realizar una transferencia, necesito la cantidad y la cuenta de destino.")
            return []

        # --- SIMULACIÓN DE PROCESO DE TRANSFERENCIA BANCARIA ---
        # Esto requeriría autenticación fuerte (2FA) y validación de la cuenta de destino.
        if cantidad > 0:
            dispatcher.utter_message(text=f"Confirmando transferencia de ${cantidad:.2f} a la cuenta {cuenta_destino}. Se te enviará un código de verificación.")
            # En un entorno real, se activaría un proceso de verificación y confirmación.
        else:
            dispatcher.utter_message(text="La cantidad a transferir debe ser positiva.")
        
        return [SlotSet("cantidad", None), SlotSet("cuenta_destino", None)]

class ActionBloquearTarjeta(Action):
    def name(self) -> Text:
        return "action_bloquear_tarjeta"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        tipo_tarjeta = tracker.get_slot("tipo_tarjeta")

        if not tipo_tarjeta:
            dispatcher.utter_message(text="¿Qué tipo de tarjeta deseas bloquear (crédito o débito)?")
            return []
        
        # --- SIMULACIÓN DE BLOQUEO DE TARJETA ---
        # Integración con el sistema de tarjetas del banco.
        dispatcher.utter_message(text=f"Hemos iniciado el proceso para bloquear tu tarjeta de {tipo_tarjeta}. Recibirás una confirmación por SMS en breve. Para reponerla, por favor visita la sucursal más cercana o llama a atención al cliente.")
        return [SlotSet("tipo_tarjeta", None)]

class ActionContactarAsesorFinanciero(Action):
    def name(self) -> Text:
        return "action_contactar_asesor_financiero"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Te pondré en contacto con un asesor financiero. Por favor, espera un momento y serás redirigido a una llamada o chat con uno de nuestros especialistas.")
        # En un entorno real, aquí se integraría con un CRM o sistema de contact center.
        return []

# ======================================================================================================
# --- SALUD: ACCIONES PARA ATENCIÓN MÉDICA ---
# ======================================================================================================

class ActionAgendarCita(Action):
    def name(self) -> Text:
        return "action_agendar_cita"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        especialidad = tracker.get_slot("especialidad")
        fecha_hora = tracker.get_slot("fecha_hora")

        if not especialidad or not fecha_hora:
            dispatcher.utter_message(text="Para agendar tu cita, necesito la especialidad médica y la fecha/hora que te gustaría.")
            return []
        
        # --- SIMULACIÓN DE AGENDA DE CITAS ---
        # Aquí se integraría con un sistema de gestión de clínicas o agenda médica.
        dispatcher.utter_message(text=f"Tu cita con {especialidad} para el {fecha_hora} ha sido agendada con éxito. Recibirás una confirmación por correo electrónico.")
        return [SlotSet("especialidad", None), SlotSet("fecha_hora", None)]

class ActionConsultarSintoma(Action):
    def name(self) -> Text:
        return "action_consultar_sintoma"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sintoma = tracker.get_slot("sintoma")

        if not sintoma:
            dispatcher.utter_message(text="Por favor, descríbeme tus síntomas con más detalle para poder buscar información.")
            return []
        
        # --- USO DE GEMINI PARA EXPLICAR SÍNTOMAS ---
        # Es crucial que el prompt indique a Gemini que NO DEBE HACER DIAGNÓSTICOS.
        prompt = f"""
        Eres un asistente de salud que proporciona información general sobre síntomas. NO ERES UN MÉDICO, NO DIAGNOSTICAS NI PRESCRIBES.
        Explica brevemente y de forma informativa sobre el siguiente síntoma: {sintoma}.
        Siempre termina tu respuesta recomendando consultar a un profesional de la salud si los síntomas persisten o empeoran.
        """
        info_sintoma = gemini_service.generate_response(prompt, domain="salud")
        dispatcher.utter_message(text=info_sintoma)
        return [SlotSet("sintoma", None)]

class ActionInformacionMedicamento(Action):
    def name(self) -> Text:
        return "action_informacion_medicamento"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        medicamento = tracker.get_slot("medicamento")

        if not medicamento:
            dispatcher.utter_message(text="¿De qué medicamento te gustaría obtener información?")
            return []
        
        # --- USO DE GEMINI PARA INFORMACIÓN DE MEDICAMENTOS ---
        prompt = f"""
        Eres un asistente de salud que proporciona información general sobre medicamentos. NO ERES UN MÉDICO, NO DIAGNOSTICAS NI PRESCRIBES.
        Explica brevemente para qué sirve y cuáles son los usos comunes del medicamento: {medicamento}.
        Aclara que siempre se debe consultar a un médico o farmacéutico antes de tomar cualquier medicamento.
        """
        info_medicamento = gemini_service.generate_response(prompt, domain="salud")
        dispatcher.utter_message(text=info_medicamento)
        return [SlotSet("medicamento", None)]

class ActionContactarEmergencia(Action):
    def name(self) -> Text:
        return "action_contactar_emergencia"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Si es una emergencia médica, por favor llama al número de emergencia local (ej. 911, 112) inmediatamente. Este asistente no puede gestionar emergencias directamente.")
        dispatcher.utter_message(text="Te recomiendo buscar ayuda profesional urgente.")
        return []

# ======================================================================================================
# --- FIN DE ACCIONES ---
# ======================================================================================================