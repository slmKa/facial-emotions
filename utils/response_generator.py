"""
Générateur de réponses empathiques basé sur l'état émotionnel
"""

import random

try:
    from .ollama_generator import OllamaGenerator
    OLLAMA_AVAILABLE = True
except:
    OLLAMA_AVAILABLE = False
    print("⚠️ Ollama non disponible, utilisation des réponses pré-définies")


class ResponseGenerator:
    def __init__(self, use_ollama=True):
        self.use_ollama = use_ollama and OLLAMA_AVAILABLE

        if self.use_ollama:
            try:
                self.ollama_gen = OllamaGenerator(model="llama2")
                print("✅ OllamaGenerator initialisé")
            except Exception as e:
                print(f"⚠️ Erreur init Ollama: {e}")
                self.use_ollama = False

        # Garder toutes les réponses existantes comme fallback
        self.responses_down = [
            "Je sens que tu traverses un moment difficile. C'est normal de se sentir comme ça parfois. 💙",
            "Prends le temps qu'il te faut. Je suis là pour toi. 🤗",
            "Tu n'es pas seul(e). Ces émotions sont temporaires. 🌈"
        ]

        self.responses_up = [
            "C'est super de te voir sourire ! Continue comme ça ! 😊",
            "Ton énergie positive est contagieuse ! ✨",
            "Profite bien de ce moment de bonheur ! 🎉"
        ]

        self.responses_neutral = [
            "Comment puis-je t'aider aujourd'hui ? 😊",
            "Je suis là si tu as besoin de parler. 💬",
            "Tout va bien de ton côté ? 🌟"
        ]

        self.followup_down = [
            "Veux-tu en parler ?",
            "Besoin d'une pause ?",
            "Que puis-je faire pour toi ?"
        ]

        self.followup_up = [
            "Continue à profiter !",
            "C'est génial !",
            "Super journée, non ?"
        ]

        self.tips_by_emotion = {
            "sad": [
                "💡 Conseil: Essaie d'écouter de la musique douce ou de faire une courte promenade.",
                "💡 Conseil: Parler à un proche peut vraiment aider.",
                "💡 Conseil: Prends quelques respirations profondes et rappelle-toi que c'est temporaire."
            ],
            "angry": [
                "💡 Conseil: Prends 5 minutes pour respirer profondément.",
                "💡 Conseil: Écris ce que tu ressens sur papier.",
                "💡 Conseil: Fais une activité physique pour évacuer la tension."
            ],
            "happy": [
                "💡 Conseil: Partage ce moment avec quelqu'un !",
                "💡 Conseil: Note ce qui te rend heureux(se) aujourd'hui.",
                "💡 Conseil: Profite pleinement de l'instant présent !"
            ],
            "neutral": [
                "💡 Conseil: C'est le moment idéal pour planifier quelque chose d'agréable.",
                "💡 Conseil: Prends du temps pour toi aujourd'hui."
            ]
        }

    def generate_response(self, mood_state, current_emotion=None, include_tip=False, context=""):
        """
        Génère une réponse basée sur l'état d'humeur

        Args:
            mood_state: "UP", "DOWN", ou "NEUTRAL"
            current_emotion: émotion spécifique détectée (optionnel)
            include_tip: inclure un conseil bien-être (optionnel)
            context: contexte additionnel pour Ollama (optionnel)

        Returns:
            str: message généré
        """
        # Tentative d'utilisation d'Ollama si activé
        if self.use_ollama:
            try:
                response = self.ollama_gen.generate_response(
                    current_emotion, 
                    mood_state, 
                    context
                )

                # Ajout d'un conseil si demandé
                if include_tip and current_emotion and current_emotion in self.tips_by_emotion:
                    tip = random.choice(self.tips_by_emotion[current_emotion])
                    response += f"\n\n{tip}"

                return response
            except Exception as e:
                print(f"⚠️ Erreur Ollama, fallback sur réponses pré-définies: {e}")
                # Continue vers le fallback

        # Fallback : Logique avec réponses pré-définies
        if mood_state == "DOWN":
            response = random.choice(self.responses_down)
        elif mood_state == "UP":
            response = random.choice(self.responses_up)
        else:
            response = random.choice(self.responses_neutral)

        # Ajout d'un conseil si demandé et émotion spécifique disponible
        if include_tip and current_emotion and current_emotion in self.tips_by_emotion:
            tip = random.choice(self.tips_by_emotion[current_emotion])
            response += f"\n\n{tip}"

        return response

    def get_followup(self, mood_state):
        """Génère une phrase de suivi"""
        if mood_state == "DOWN":
            return random.choice(self.followup_down)
        elif mood_state == "UP":
            return random.choice(self.followup_up)
        else:
            return "N'hésite pas à me parler si quelque chose change. 😊"

    def get_notification_message(self, mood_state, duration_minutes):
        """
        Génère un message de notification basé sur la durée
        d'un état émotionnel
        """
        if mood_state == "DOWN" and duration_minutes > 5:
            return (
                f"⚠️ Tu sembles avoir le moral bas depuis {duration_minutes} minutes. "
                "Pense à faire une pause, prendre l'air, ou parler à quelqu'un de confiance."
            )
        elif mood_state == "UP" and duration_minutes > 10:
            return (
                f"🎉 Tu es dans un super état d'esprit depuis {duration_minutes} minutes ! "
                "Continue à profiter de ce moment positif !"
            )
        return None
