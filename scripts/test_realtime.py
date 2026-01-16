"""
Script de test de détection d'émotions en temps réel
Appuie sur 'q' pour quitter
"""

import cv2
import sys
import os

# Ajouter le dossier parent au path

from utils.emotion_detector import EmotionDetector

def main():
    print("="*60)
    print("TEST DÉTECTION ÉMOTIONS EN TEMPS RÉEL")
    print("="*60)
    print("\n📹 Initialisation de la webcam...")
    
    # Initialisation du détecteur
    detector = EmotionDetector()
    
    # Ouverture webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Impossible d'ouvrir la webcam!")
        return
    
    print("✅ Webcam ouverte!")
    print("\n💡 Instructions:")
    print("   - La détection se fait en temps réel")
    print("   - Appuie sur 'q' pour quitter")
    print("   - Appuie sur 's' pour voir l'état d'humeur actuel\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Erreur de lecture de la frame")
            break
        
        # Détection d'émotions
        annotated_frame, emotions = detector.detect_emotion(frame)
        
        # Affichage de l'état d'humeur sur la frame
        mood_state = detector.get_mood_state()
        mood_color = {
            "UP": (0, 255, 0),      # Vert
            "DOWN": (0, 0, 255),    # Rouge
            "NEUTRAL": (200, 200, 200)  # Gris
        }
        
        cv2.putText(
            annotated_frame,
            f"Mood: {mood_state}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            mood_color[mood_state],
            2
        )
        
        # Affichage du nombre d'émotions détectées
        cv2.putText(
            annotated_frame,
            f"Faces detected: {len(emotions)}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        cv2.imshow('Emotion Detection - Press Q to quit', annotated_frame)
        
        # Gestion clavier
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("\n🛑 Arrêt demandé par l'utilisateur")
            break
        elif key == ord('s'):
            print(f"\n📊 État actuel: {mood_state}")
            if emotions:
                for idx, emo in enumerate(emotions, 1):
                    print(f"   Visage {idx}: {emo['emotion']} ({emo['confidence']*100:.1f}%)")
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n✅ Test terminé ({frame_count} frames traitées)")
    print("="*60)

if __name__ == "__main__":
    main()
