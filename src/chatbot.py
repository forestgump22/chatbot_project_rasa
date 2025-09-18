import pickle
import random 
import os 
import numpy as np

class Chatbot:
    def __init__(self, model_dir='models/'):
        self.model_dir = model_dir
        self.model = None
        self.temperature = 0.7

        self.load_model()

    def load_model(self):
        try:
            model_path = os.path.join(self.model_dir, 'chatbot_model.pkl')
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # carga vectorizador
            vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
            with open(vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # cargar metadata
            metadata_path = os.path.join(self.model_dir, 'metadata.pkl')
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.intent_labels = metadata['intent_labels']
                self.intents = metadata['intents']
            
            print("Modelo cargado exitosamente")
            return True
        except FileNotFoundError:
            print("No se encontro modelo entrenado. Ejecuta el entrenamiento primero.")
        except Exception as e:
            print(f"Error encontrado: {e}")
            return False
    
    def predict_intent(self, message):
        """Predice la intencion del mensaje"""
        if not self.model or not self.vectorizer:
            return None, 0.0
        
        #Vectorizar el mensaje
        message_vector = self.vectorizer.transform([message])

        # Prediccion con probabilidades
        probabilities = self.model.predict_proba(message_vector)[0]
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]

        intent = self.intent_labels[predicted_class]

        return intent, confidence
    
    def get_fallback_response(self):
        """Respuesta cuando no se puede clasificar la intencion"""
        fallback_responses = [
            "No estoy seguro de como responder a eso. Puedes formalizar tu pregunta?",
            "Disculpa, no entendi tu pregunta. Puedes ser mas especifico?",
            "Hmm, no tengo una respuesta clara para eso. Hay algo mas en lo que pueda ayudarte?"
        ]
        return random.choice(fallback_responses)
    
    def chat(self):
        """Interfaz de chat por consola"""
        print("Hola! soy tu chatbot. Escribe 'quit' para salir.\n")

        while True:
            user_input = input("Tu: ").strip()

            if user_input.lower() in ['quit', 'salir','exit']:
                print("Bot: !Hasta luego")
                break

            response = self.get_response(user_input)
            print(f"Bot: {response}\n")
    
    def set_confidence_threshold(self, threshold):
        """Ajusta el umbral de confianza"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def get_model_info(self):
        """Retorno de informacion sobre el modelo cargado"""
        if not self.model:
            return "No hay modelo cargado"
        
        info = {
            'intents_disponibles': self.intent_labels,
            'numero_intents': len(self.intent_labels),
            'umbral_confianza': self.confidence_threshold
        }
        return info
    
#Script

if __name__ == "__main__":
    bot = Chatbot()
    if bot.model:
        bot.chat()
    else:
        print("Primero ejecutar modelo de training")


            
            