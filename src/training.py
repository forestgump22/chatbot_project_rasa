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

        
