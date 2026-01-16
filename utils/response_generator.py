"""
Générateur de réponses empathiques basé sur l'état émotionnel
"""

import random

class ResponseGenerator:
    def __init__(self):
        # Réponses pour état DOWN (émotions négatives)
        self.responses_down = [
            "Je vois que tu ne te sens pas au top en ce moment... Veux-tu me parler de ce qui te tracasse ? 😔",
            "Tu sembles avoir le moral un peu bas. N'hésite pas à partager ce qui te pèse, je suis là pour t'écouter. 💙",
            "Je sens que quelque chose te préoccupe. Parfois, en parler aide à y voir plus clair. Je t'écoute. 🤗",
            "Les moments difficiles font partie de la vie, mais tu n'es pas seul(e). Raconte-moi ce qui ne va pas. 💪",
            "Tu as l'air stressé(e) ou triste. Prendre une pause pour en parler peut vraiment aider. Je suis là. 😊",
            "Je remarque que ton humeur n'est pas terrible... Un coup de blues ? Parlons-en ensemble. 🌙",
            "Ça a l'air d'être une période compliquée pour toi. N'hésite pas à te confier, ça fait du bien. ❤️",
            "Je sens que tu as besoin de soutien. Qu'est-ce qui te rend triste ou anxieux(se) en ce moment ? 🫂",
            "Tu sembles porter un poids sur les épaules. Libère-toi, exprime ce que tu ressens ! 🌻",
            "Les émotions négatives sont normales. Parlons-en, et trouvons ensemble des pistes pour te sentir mieux. 🌈"
        ]
        
        # Réponses pour état UP (émotions positives)
        self.responses_up = [
            "Super ! Tu as l'air en pleine forme aujourd'hui ! 😄 Raconte-moi ce qui te rend heureux(se) !",
            "Wow, quelle belle énergie positive ! Continue comme ça, tu rayonnes ! ✨",
            "Je sens que tu as le moral au beau fixe ! C'est génial, profite de ce moment ! 🎉",
            "Tu as l'air vraiment content(e) ! Partage-moi cette bonne nouvelle qui te fait sourire ! 🌟",
            "C'est un plaisir de te voir dans cet état d'esprit ! Qu'est-ce qui te met de si bonne humeur ? 😊",
            "Excellent ! Tu dégages une énergie incroyable ! Continue sur cette lancée ! 🚀",
            "Tu as l'air radieux(se) aujourd'hui ! C'est communicatif, merci de partager cette joie ! 💫",
            "Fantastique ! Tu es dans une super dynamique positive ! Raconte-moi ton secret ! 🎊",
            "Je vois que la vie te sourit en ce moment ! Profite à fond de ces beaux moments ! 🌞",
            "Quelle belle énergie ! Tu illumines la pièce ! Continue comme ça ! 🌺"
        ]
        
        # Réponses pour état NEUTRAL
        self.responses_neutral = [
            "Tu as l'air calme et serein(e) aujourd'hui. Comment puis-je t'aider ? 😊",
            "Tu sembles dans un état d'esprit neutre. Comment se passe ta journée ? 🙂",
            "Je suis là pour discuter si tu en as envie. Comment te sens-tu vraiment ? 💬",
            "Tu as l'air plutôt stable émotionnellement. Y a-t-il quelque chose dont tu veux parler ? 🤔",
            "Tu sembles équilibré(e) aujourd'hui. Besoin d'échanger sur quelque chose en particulier ? 💭",
            "Tout a l'air de bien aller pour toi. Veux-tu discuter ou simplement te détendre ? ☺️",
            "Je te sens dans un état d'esprit tranquille. Comment puis-je rendre ta journée meilleure ? 🌿",
            "Tu as l'air zen ! C'est agréable. N'hésite pas si tu veux discuter de quelque chose. 🧘",
        ]
        
        # Phrases de suivi pour DOWN
        self.followup_down = [
            "Prends ton temps, il n'y a pas d'urgence. Exprime-toi librement. 🕊️",
            "Respire profondément. Parfois, ça aide de mettre des mots sur nos émotions. 🌬️",
            "Tu peux tout me dire, sans jugement. Je suis là pour t'accompagner. 💙",
            "Même les jours difficiles finissent par passer. Tu es plus fort(e) que tu ne le penses. 💪",
            "N'oublie pas : demander de l'aide ou en parler est un signe de force, pas de faiblesse. 🦋",
        ]
        
        # Phrases de suivi pour UP
        self.followup_up = [
            "Continue à cultiver cette belle énergie positive ! 🌈",
            "Ces moments de bonheur méritent d'être savourés pleinement ! 🍃",
            "Ta joie est contagieuse, merci de la partager ! 😄",
            "Garde précieusement ce souvenir heureux pour les jours plus difficiles. 📸",
            "Tu mérites tout ce bonheur ! Profite-en au maximum ! 🎁",
        ]
        
        # Conseils bien-être selon émotion spécifique
        self.tips_by_emotion = {
            'sad': [
                "💡 Astuce : Écouter de la musique douce ou faire une activité créative peut aider à gérer la tristesse.",
                "💡 Conseil : Prendre l'air et marcher 10-15 minutes peut vraiment remonter le moral.",
                "💡 Idée : Contacte un ami ou un proche, le soutien social est précieux dans ces moments.",
            ],
            'angry': [
                "💡 Technique : Essaie la respiration profonde : inspire 4 sec, retiens 4 sec, expire 6 sec.",
                "💡 Conseil : L'exercice physique (sport, marche rapide) aide à évacuer la colère sainement.",
                "💡 Astuce : Écris ce qui te met en colère sur papier, puis froisse-le et jette-le (symbolique).",
            ],
            'fear': [
                "💡 Technique : Identifie précisément ce qui te fait peur, souvent ça aide à relativiser.",
                "💡 Conseil : Parle à quelqu'un de confiance de tes craintes, ça les rend moins intenses.",
                "💡 Astuce : La méditation de pleine conscience peut apaiser l'anxiété (apps : Petit Bambou, Calm).",
            ],
            'happy': [
                "💡 Idée : Note ce moment de bonheur dans un journal de gratitude !",
                "💡 Conseil : Partage ta joie avec tes proches, ça renforce les liens positifs !",
                "💡 Astuce : Prends une photo mentale de ce moment pour le revivre plus tard !",
            ],
            'surprise': [
                "💡 Les surprises positives sont excellentes pour le moral ! Profite de cette énergie ! ⚡",
            ],
            'disgust': [
                "💡 Identifie ce qui te dérange et, si possible, éloigne-toi-en physiquement ou mentalement.",
            ],
            'neutral': [
                "💡 Un état neutre est sain ! Tu peux en profiter pour planifier ou te recentrer. 🧘",
            ]
        }
    
    def generate_response(self, mood_state, current_emotion=None, include_tip=False):
        """
        Génère une réponse basée sur l'état d'humeur
        
        Args:
            mood_state: "UP", "DOWN", ou "NEUTRAL"
            current_emotion: émotion spécifique détectée (optionnel)
            include_tip: inclure un conseil bien-être (optionnel)
        
        Returns:
            str: message généré
        """
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
