import re
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

#Descarga recursos necesarios de NLTK
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextPreprocessor:
    def __init__(self):
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))

    def clean_text(self, text):
        """Limpia y normaliza el texto"""
        #Convertir a minusculas
        text = text.lower()

        #Remover acentos
        text = self.remove_accents(text)

        #Remover caracteres especiales pero mantener espacios
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

        #Remover espacios extra
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    
    def remove_accents(self, text):
        """Remueve acentos del texto"""
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')
    
    #Separa cada palabra de la oracion
    def tokenize(self, text):
        """Tokeniza el texto"""
        tokens = nltk.word_tokenize(text)
        # Filtrar stopwords y aplicar stemming
        stemmed_tokens = [
            self.stemmer.stem(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 2
        ]
        return ' '.join(stemmed_tokens)
    
    def preprocess(self, text):
        """Proceso completo de preprocesamiento"""
        cleaned = self.clean_text(text)
        processed = self.tokenize(cleaned)
        return processed

class IntentVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words=None #Ya se manejo stopwors en este mismo archivo
        )
        self.preprocessor = TextPreprocessor()

    def fit_transform(self, texts):
        """Ajusta el vectorizador y transforma los textos"""
        processed_texts = [self.preprocessor.preprocess(text) for text in texts]
        return self.vectorizer.fit_transform(processed_texts)
    
    def transform(self, texts):
        """Transforma los textos usando el vectorizador"""
        if isinstance(texts, str):
            texts = [texts]
        processed_texts = [self.preprocessor.preprocess(text) for text in texts]
        return self.vectorizer.transform(processed_texts)


