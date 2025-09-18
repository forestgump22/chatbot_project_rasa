import json 
import pickle
import os 
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

import numpy as np
from .preprocessing import IntentVectorizer

class ChatbotTrainer:
    def __init__(self):
        self.vectorizer = IntentVectorizer()
        self.model = SVC(kernel='linear', probability=True, random_state=42)
        self.intents = None
        self.intent_labels = []
    
    def load_intents(self, filepath):
        """Carga los intents desde un archivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.intents = data['intents']
        return self.intents 
    
    def prepare_training_data(self):
        """Preparar los datos para entrenamiento"""
        patterns = []
        labels = []

        for intent in self.intents:
            for pattern in intent['patterns']:
                patterns.append(pattern)
                labels.append(intent['tag'])
        
        #Crear mapeo de labels/etiquetas unicos
        self.intent_labels = list(set(labels))
        label_to_index = {label:idx for idx,label in enumerate(self.intent_labels)}

        y = [label_to_index[label] for label in labels]

        return patterns, y
    
    def train(self, intents_filepath):
        """Entrena el modelo completo"""
        print("Cargando intents ")
        self.load_intents(intents_filepath)

        print("Preparando datos de entrenamiento")
        x_text, y = self.prepare_training_data()

        print("Vectorizando texto")
        x = self.vectorizer.fit_transform(x_text)

        print("Dividiendo datos para entrenamiento y prueba")
        X_train, X_test, y_train, y_test = train_test_split(x,y,test_size=0.2, random_state=42, stratify=y)

        print("Entrenando modelo")
        self.model.fit(X_train, y_train)

        #Evaluacion
        print("\nEvaluando modelo")
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Precision: {accuracy:.4f}")

        print("\nReporte de clasificacion:")
        target_names = [self.intent_labels[i] for i in sorted(set(y_test))]
        print(classification_report(y_test, y_pred, target_names=target_names))

        return accuracy
    
    def save_model(self, model_dir):
        """Guarda el modelo y componentes necesarios"""
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        #Guardamos modelo
        model_path = os.path.join(model_dir, 'chatbot_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        #Guardamos vectorizador
        vectorizer_path = os.path.join(model_dir, 'vectorizer.pkl')
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        #Guardamos labels e intents
        metadata = {
            'intent_labels': self.intent_labels,
            'intents': self.intents
        }
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

        print(f"Modelo guardado en {model_dir}")

#Codigo principal para entrenamiento del modelo.

if __name__ == "__main__":
    trainer = ChatbotTrainer()

    #entrenamiento del modelo
    trainer.train('../data/intents.json')

    #Guardar el modelo
    trainer.save_model('../models/')



        
