"""
Module de détection d'émotions faciales en temps réel
"""

import cv2
import numpy as np
from tensorflow.keras.models import load_model
import json
import os
from collections import deque

class EmotionDetector:
    def __init__(self, model_path="models/emotion_model.h5"):
        print("🔄 Chargement du modèle d'émotions...")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modèle non trouvé: {model_path}\n"
                "Lance d'abord: python scripts/1_train_model.py"
            )
        
        self.model = load_model(model_path)
        
        # Chargement labels émotions
        labels_path = "models/emotion_labels.json"
        with open(labels_path, 'r', encoding='utf-8') as f:
            emotion_labels = json.load(f)
        
        self.emotion_labels = {int(k): v for k, v in emotion_labels.items()}
        
        # Détecteur de visage Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Buffer pour lisser les prédictions
        self.emotion_buffer = deque(maxlen=10)
        
        print("✅ Détecteur d'émotions prêt!")
    
    def detect_emotion(self, frame):
        """
        Détecte les émotions sur une frame
        Returns: (frame_annotated, emotions_detected)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(48, 48)
        )
        
        emotions_detected = []
        
        for (x, y, w, h) in faces:
            # Extraction et prétraitement du visage
            face_roi = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_roi, (48, 48))
            face_normalized = face_resized.astype('float32') / 255.0
            face_input = np.expand_dims(face_normalized, axis=0)
            face_input = np.expand_dims(face_input, axis=-1)
            
            # Prédiction
            predictions = self.model.predict(face_input, verbose=0)[0]
            emotion_idx = np.argmax(predictions)
            confidence = predictions[emotion_idx]
            emotion_label = self.emotion_labels[emotion_idx]
            
            # Ajout au buffer
            self.emotion_buffer.append(emotion_label)
            
            # Annotation du visage
            color = self._get_emotion_color(emotion_label)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Texte émotion + confiance
            text = f"{emotion_label}: {confidence*100:.1f}%"
            cv2.putText(frame, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            emotions_detected.append({
                'emotion': emotion_label,
                'confidence': float(confidence),
                'bbox': (x, y, w, h)
            })
        
        return frame, emotions_detected
    
    def get_mood_state(self):
        """
        Détermine l'état d'humeur global (UP/DOWN/NEUTRAL)
        basé sur l'historique récent des émotions
        """
        if len(self.emotion_buffer) == 0:
            return "NEUTRAL"
        
        # Classification des émotions
        negative_emotions = ['angry', 'sad', 'fear', 'disgust']
        positive_emotions = ['happy', 'surprise']
        
        negative_count = sum(1 for e in self.emotion_buffer if e in negative_emotions)
        positive_count = sum(1 for e in self.emotion_buffer if e in positive_emotions)
        
        total = len(self.emotion_buffer)
        negative_ratio = negative_count / total
        positive_ratio = positive_count / total
        
        # Seuils de décision
        if negative_ratio > 0.6:
            return "DOWN"
        elif positive_ratio > 0.5:
            return "UP"
        else:
            return "NEUTRAL"
    
    def _get_emotion_color(self, emotion):
        """Retourne une couleur BGR selon l'émotion"""
        color_map = {
            'angry': (0, 0, 255),      # Rouge
            'disgust': (128, 0, 128),  # Violet
            'fear': (255, 0, 255),     # Magenta
            'happy': (0, 255, 0),      # Vert
            'sad': (255, 0, 0),        # Bleu
            'surprise': (0, 255, 255), # Jaune
            'neutral': (200, 200, 200) # Gris
        }
        return color_map.get(emotion, (255, 255, 255))
