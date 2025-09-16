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
            
            