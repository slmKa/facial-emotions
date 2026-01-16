"""
Générateur de réponses via Ollama LLM
"""
import requests
import json
import random

class OllamaGenerator:
    def __init__(self, model="llama2", base_url="http://localhost:11434"):
        """
        Initialise le générateur Ollama
        
        Args:
            model: Nom du modèle Ollama (llama2, mistral, etc.)
            base_url: URL du serveur Ollama
        """
        self.model = model
        self.base_url = base_url
        self.is_available = self._check_availability()
        
    def _check_availability(self):
        """Vérifie si Ollama est disponible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def build_prompt(self, emotion, mood_state, user_message=""):
        """
        Construit un prompt contextualisé basé sur l'émotion détectée
        
        Args:
            emotion: Émotion détectée (happy, sad, angry, etc.)
            mood_state: État d'humeur (UP, DOWN, NEUTRAL)
            user_message: Message de l'utilisateur (optionnel)
        
        Returns:
            str: Prompt formaté pour Ollama
        """
        emotion_fr = {
            'happy': 'heureux/heureuse',
            'sad': 'triste',
            'angry': 'en colère',
            'fear': 'anxieux/anxieuse',
            'surprise': 'surpris(e)',
            'disgust': 'dégoûté(e)',
            'neutral': 'neutre/calme'
        }
        
        emotion_text = emotion_fr.get(emotion, emotion)
        
        system_context = f"""Tu es un assistant empathique et bienveillant. 
L'utilisateur semble {emotion_text} (état: {mood_state}).
Génère une réponse courte (2-3 phrases maximum) en français qui:
- Est empathique et adaptée à son état émotionnel
- L'encourage ou le réconforte selon son humeur
- Reste naturelle et humaine"""

        if user_message:
            prompt = f"{system_context}\n\nMessage de l'utilisateur: \"{user_message}\"\n\nRéponds de manière empathique:"
        else:
            prompt = f"{system_context}\n\nGénère une phrase d'accueil empathique:"
        
        return prompt
    
    def generate_response(self, emotion, mood_state, user_message=""):
        """
        Génère une réponse via Ollama
        
        Args:
            emotion: Émotion détectée
            mood_state: État d'humeur (UP/DOWN/NEUTRAL)
            user_message: Message utilisateur (contexte)
        
        Returns:
            str: Réponse générée
        """
        # Si Ollama n'est pas disponible, utiliser fallback
        if not self.is_available:
            print("⚠️ Ollama non disponible, utilisation du fallback")
            return self._fallback_response(mood_state)
        
        prompt = self.build_prompt(emotion, mood_state, user_message)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                # Nettoyer la réponse
                if generated_text:
                    return generated_text
                else:
                    return self._fallback_response(mood_state)
            else:
                print(f"❌ Erreur Ollama: {response.status_code}")
                return self._fallback_response(mood_state)
                
        except requests.exceptions.Timeout:
            print("⏱️ Timeout Ollama")
            return self._fallback_response(mood_state)
        except Exception as e:
            print(f"❌ Erreur Ollama: {e}")
            return self._fallback_response(mood_state)
    
    def _fallback_response(self, mood_state):
        """Réponses de secours si Ollama ne répond pas"""
        fallbacks = {
            "DOWN": [
                "Je suis là pour t'écouter. Comment puis-je t'aider ? 💙",
                "Je vois que tu ne vas pas au top. Veux-tu en parler ? 😔",
                "Prends ton temps, je suis là pour t'accompagner. 🤗"
            ],
            "UP": [
                "C'est super de te voir de bonne humeur ! 😊",
                "Quelle belle énergie positive ! Continue comme ça ! ✨",
                "Tu rayonnes aujourd'hui ! Raconte-moi ce qui te rend heureux(se) ! 🌟"
            ],
            "NEUTRAL": [
                "Comment puis-je t'aider aujourd'hui ? 😊",
                "Je suis là pour discuter si tu en as envie. 💬",
                "Tu as l'air serein(e). Comment te sens-tu ? 🙂"
            ]
        }
        
        responses = fallbacks.get(mood_state, fallbacks["NEUTRAL"])
        return random.choice(responses)
    
    def test_connection(self):
        """Test la connexion à Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Ollama connecté ! Modèles disponibles:")
                for model in models:
                    print(f"  - {model['name']}")
                return True
            else:
                print(f"❌ Ollama non accessible (status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Impossible de se connecter à Ollama: {e}")
            return False
