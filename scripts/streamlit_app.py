"""
Application complète de chatbot émotionnel avec Streamlit
Lance avec: streamlit run scripts/3_streamlit_app.py
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import time

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.emotion_detector import EmotionDetector
from utils.response_generator import ResponseGenerator
from utils.database import Database

# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Chatbot Émotionnel ",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONNALISÉ
# ============================================================

st.markdown("""
<style>
/* ========== THEME SOMBRE GLOBAL ========== */

/* Fond global de l'app */
.stApp {
    background-color: #0e1117;
    color: #e6e6e6;
}

/* Conteneur principal */
.main {
    background-color: #0e1117;
    color: #e6e6e6;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}
section[data-testid="stSidebar"] * {
    color: #e6e6e6 !important;
}

/* Titres / textes généraux */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: #e6e6e6;
}

/* Inputs */
textarea, input, .stTextInput input {
    background-color: #111827 !important;
    color: #e6e6e6 !important;
    border: 1px solid #2a3441 !important;
}

/* Zone de chat (tes classes existantes) */
.chat-message {
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

/* Messages */
.user-message {
    background-color: #2563eb;  /* bleu plus lisible en dark */
    color: #ffffff;
    margin-left: 20%;
}

.bot-message {
    background-color: #1f2937;  /* gris foncé */
    color: #e6e6e6;
    margin-right: 20%;
    border: 1px solid #2a3441;
}

/* Boxes mood */
.emotion-box {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    font-weight: bold;
}

.mood-up {
    background-color: rgba(34, 197, 94, 0.15);
    color: #d1fae5;
    border-left: 5px solid #22c55e;
}

.mood-down {
    background-color: rgba(239, 68, 68, 0.15);
    color: #fee2e2;
    border-left: 5px solid #ef4444;
}

.mood-neutral {
    background-color: rgba(148, 163, 184, 0.12);
    color: #e2e8f0;
    border-left: 5px solid #94a3b8;
}

/* Boutons */
.stButton>button {
    width: 100%;
    background-color: #22c55e;
    color: #0b0f14;
    font-weight: bold;
    border: 0;
}
.stButton>button:hover {
    background-color: #16a34a;
    color: #0b0f14;
}

/* Cartes Streamlit (metrics, alertes, etc.) */
div[data-testid="stMetric"] {
    background-color: #111827;
    border: 1px solid #2a3441;
    padding: 12px;
    border-radius: 10px;
}

/* Dataframe (fond sombre) */
div[data-testid="stDataFrame"] {
    background-color: #111827;
    border: 1px solid #2a3441;
    border-radius: 10px;
}

/* Onglets */
button[data-baseweb="tab"] {
    color: #e6e6e6 !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALISATION SESSION STATE
# ============================================================

if 'detector' not in st.session_state:
    st.session_state.detector = None

if 'response_gen' not in st.session_state:
    st.session_state.response_gen = ResponseGenerator()

if 'db' not in st.session_state:
    st.session_state.db = Database()

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'session_id' not in st.session_state:
    st.session_state.session_id = None

if 'current_emotion' not in st.session_state:
    st.session_state.current_emotion = None

if 'current_mood' not in st.session_state:
    st.session_state.current_mood = "NEUTRAL"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'emotion_history' not in st.session_state:
    st.session_state.emotion_history = []

if 'last_notification_time' not in st.session_state:
    st.session_state.last_notification_time = None

if 'webcam_active' not in st.session_state:
    st.session_state.webcam_active = False

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

@st.cache_resource
def load_detector():
    """Charge le détecteur d'émotions (une seule fois)"""
    try:
        detector = EmotionDetector()
        return detector
    except Exception as e:
        st.error(f"❌ Erreur de chargement du modèle: {e}")
        return None

def check_notification_trigger():
    """Vérifie si une notification doit être envoyée"""
    if st.session_state.current_mood == "DOWN":
        if len(st.session_state.emotion_history) >= 5:
            # Dernières 5 émotions
            recent = st.session_state.emotion_history[-5:]
            negative_count = sum(1 for e in recent if e['mood'] == 'DOWN')
            
            # Si 80%+ des dernières émotions sont DOWN
            if negative_count >= 4:
                # Vérifier qu'on n'a pas déjà notifié récemment
                now = datetime.now()
                if (st.session_state.last_notification_time is None or 
                    (now - st.session_state.last_notification_time).seconds > 300):  # 5 min
                    
                    duration = len([e for e in st.session_state.emotion_history if e['mood'] == 'DOWN'])
                    
                    notif_msg = st.session_state.response_gen.get_notification_message(
                        "DOWN", duration
                    )
                    
                    if notif_msg and st.session_state.user_id:
                        st.session_state.db.create_notification(
                            st.session_state.user_id,
                            "mood_alert",
                            notif_msg
                        )
                        st.session_state.last_notification_time = now
                        return notif_msg
    
    return None

def display_chat_message(role, message, emotion=None):
    """Affiche un message de chat stylisé"""
    if role == "user":
        emotion_tag = f" [{emotion}]" if emotion else ""
        st.markdown(
            f'<div class="chat-message user-message">👤 Vous{emotion_tag}: {message}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message bot-message">🤖 Assistant: {message}</div>',
            unsafe_allow_html=True
        )

def display_mood_state(mood):
    """Affiche l'état d'humeur actuel"""
    mood_class = f"mood-{mood.lower()}"
    mood_emoji = {"UP": "😊", "DOWN": "😔", "NEUTRAL": "😐"}
    
    st.markdown(
        f'<div class="emotion-box {mood_class}">'
        f'{mood_emoji[mood]} État d\'humeur actuel: <strong>{mood}</strong>'
        f'</div>',
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR - CONNEXION & INFOS
# ============================================================

with st.sidebar:
    st.title("🤖 Chatbot Émotionnel")
    st.markdown("---")
    
    # Connexion utilisateur
    st.subheader("👤 Connexion")
    username = st.text_input("Nom d'utilisateur", value="user_demo")
    
    if st.button("Se connecter"):
        if username:
            st.session_state.user_id = st.session_state.db.get_or_create_user(username)
            st.session_state.session_id = st.session_state.db.create_session(st.session_state.user_id)
            st.success(f"✅ Connecté en tant que: {username}")
            st.rerun()
        else:
            st.error("⚠️ Entre un nom d'utilisateur")
    
    if st.session_state.user_id:
        st.info(f"✅ Connecté: {username}")
        
        st.markdown("---")
        
        # Charger le détecteur
        if st.session_state.detector is None:
            with st.spinner("Chargement du modèle..."):
                st.session_state.detector = load_detector()
        
        if st.session_state.detector:
            st.success("✅ Modèle chargé")
        
        st.markdown("---")
        
        # Statistiques
        st.subheader("📊 Statistiques")
        stats = st.session_state.db.get_user_stats(st.session_state.user_id, limit=50)
        
        if stats:
            emotions_list = [s[0] for s in stats]
            emotion_counts = pd.Series(emotions_list).value_counts()
            
            st.write(f"**Total détections:** {len(stats)}")
            st.write("**Répartition:**")
            for emotion, count in emotion_counts.items():
                st.write(f"- {emotion}: {count}")
        else:
            st.write("Aucune donnée encore")
        
        st.markdown("---")
        
        # Notifications
        st.subheader("🔔 Notifications")
        notifs = st.session_state.db.get_unread_notifications(st.session_state.user_id)
        
        if notifs:
            for notif in notifs:
                notif_id, notif_type, message, timestamp = notif
                st.warning(f"**{timestamp}**\n{message}")
                if st.button(f"Marquer comme lu", key=f"notif_{notif_id}"):
                    st.session_state.db.mark_notification_read(notif_id)
                    st.rerun()
        else:
            st.info("Aucune nouvelle notification")

# ============================================================
# ZONE PRINCIPALE
# ============================================================

st.title("😊 Chatbot Émotionnel Empathique")
st.markdown("Un assistant qui s'adapte à tes émotions en temps réel")

if not st.session_state.user_id:
    st.warning("⚠️ Connecte-toi d'abord dans la barre latérale")
    st.stop()

if not st.session_state.detector:
    st.error("❌ Le modèle n'a pas pu être chargé. Lance d'abord: `python scripts/1_train_model.py`")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📸 Détection Webcam", "📈 Historique"])

# ============================================================
# TAB 1: CHAT
# ============================================================

with tab1:
    st.subheader("💬 Conversation")
    
    # Affichage état d'humeur
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_mood_state(st.session_state.current_mood)
    
    with col2:
        if st.session_state.current_emotion:
            st.metric(
                "Dernière émotion",
                st.session_state.current_emotion['emotion'],
                f"{st.session_state.current_emotion['confidence']*100:.1f}%"
            )
    
    st.markdown("---")
    
    # Zone de conversation
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Salut ! Active ta webcam ou envoie un message pour commencer.")
        else:
            for msg in st.session_state.chat_history:
                display_chat_message(
                    msg['role'],
                    msg['message'],
                    msg.get('emotion')
                )
    
    st.markdown("---")
    
    # Zone de saisie
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Écris quelque chose...",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Envoyer", use_container_width=True)
    
    if send_button and user_input:
        # Enregistrer message utilisateur
        st.session_state.chat_history.append({
            'role': 'user',
            'message': user_input,
            'emotion': st.session_state.current_emotion['emotion'] if st.session_state.current_emotion else None
        })
        
        if st.session_state.session_id:
            st.session_state.db.log_message(
                st.session_state.session_id,
                'user',
                user_input,
                st.session_state.current_emotion['emotion'] if st.session_state.current_emotion else None
            )
        
        # Générer réponse du bot
        include_tip = len(st.session_state.chat_history) % 3 == 0  # Un conseil tous les 3 échanges
        
        bot_response = st.session_state.response_gen.generate_response(
            st.session_state.current_mood,
            st.session_state.current_emotion['emotion'] if st.session_state.current_emotion else None,
            include_tip=include_tip
        )
        
        st.session_state.chat_history.append({
            'role': 'bot',
            'message': bot_response
        })
        
        if st.session_state.session_id:
            st.session_state.db.log_message(
                st.session_state.session_id,
                'bot',
                bot_response
            )
        
        st.rerun()

# ============================================================
# TAB 2: DÉTECTION WEBCAM
# ============================================================

with tab2:
    st.subheader("📸 Détection d'émotions en temps réel")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_webcam = st.button("▶️ Démarrer la webcam", use_container_width=True)
    
    with col2:
        stop_webcam = st.button("⏹️ Arrêter la webcam", use_container_width=True)
    
    if start_webcam:
        st.session_state.webcam_active = True
    
    if stop_webcam:
        st.session_state.webcam_active = False
    
    st.markdown("---")
    
    frame_placeholder = st.empty()
    info_placeholder = st.empty()
    
    if st.session_state.webcam_active:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Impossible d'ouvrir la webcam!")
            st.session_state.webcam_active = False
        else:
            stframe = st.empty()
            
            while st.session_state.webcam_active:
                ret, frame = cap.read()
                
                if not ret:
                    st.error("❌ Erreur de lecture webcam")
                    break
                
                # Détection
                annotated_frame, emotions = st.session_state.detector.detect_emotion(frame)
                mood_state = st.session_state.detector.get_mood_state()
                
                # Mise à jour session state
                if emotions:
                    st.session_state.current_emotion = emotions[0]
                    st.session_state.current_mood = mood_state
                    
                    # Log dans DB
                    if st.session_state.session_id:
                        st.session_state.db.log_emotion(
                            st.session_state.session_id,
                            emotions[0]['emotion'],
                            emotions[0]['confidence'],
                            mood_state
                        )
                    
                    # Ajouter à l'historique
                    st.session_state.emotion_history.append({
                        'emotion': emotions[0]['emotion'],
                        'mood': mood_state,
                        'timestamp': datetime.now()
                    })
                    
                    # Limiter l'historique à 100 entrées
                    if len(st.session_state.emotion_history) > 100:
                        st.session_state.emotion_history.pop(0)
                
                # Vérifier notifications
                notif = check_notification_trigger()
                if notif:
                    st.toast(notif, icon="⚠️")
                
                # Convertir BGR -> RGB pour Streamlit
                frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                
                # Affichage
                stframe.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Infos
                info_placeholder.info(
                    f"🎭 État: **{mood_state}** | "
                    f"Émotion: **{emotions[0]['emotion'] if emotions else 'Aucune'}** | "
                    f"Confiance: **{emotions[0]['confidence']*100:.1f}%** " if emotions else ""
                )
                
                time.sleep(0.03)  # ~30 FPS
            
            cap.release()
            st.success("✅ Webcam arrêtée")
    else:
        frame_placeholder.info("📷 Clique sur 'Démarrer la webcam' pour lancer la détection")

# ============================================================
# TAB 3: HISTORIQUE
# ============================================================

with tab3:
    st.subheader("📈 Historique de la session")
    
    if st.session_state.session_id:
        # Historique des émotions
        st.markdown("### 🎭 Émotions détectées")
        
        if st.session_state.emotion_history:
            df_emotions = pd.DataFrame(st.session_state.emotion_history)
            
            # Stats globales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total détections", len(df_emotions))
            
            with col2:
                mood_counts = df_emotions['mood'].value_counts()
                dominant_mood = mood_counts.idxmax() if not mood_counts.empty else "N/A"
                st.metric("Humeur dominante", dominant_mood)
            
            with col3:
                emotion_counts = df_emotions['emotion'].value_counts()
                top_emotion = emotion_counts.idxmax() if not emotion_counts.empty else "N/A"
                st.metric("Émotion principale", top_emotion)
            
            # Graphiques
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Répartition des émotions**")
                st.bar_chart(df_emotions['emotion'].value_counts())
            
            with col2:
                st.markdown("**Répartition de l'humeur**")
                st.bar_chart(df_emotions['mood'].value_counts())
            
            # Tableau détaillé
            st.markdown("---")
            st.markdown("**Détails chronologiques**")
            st.dataframe(
                df_emotions[['timestamp', 'emotion', 'mood']].tail(20),
                use_container_width=True
            )
        else:
            st.info("Aucune émotion détectée pour le moment")
        
        st.markdown("---")
        
        # Historique des messages
        st.markdown("### 💬 Historique des conversations")
        
        if st.session_state.chat_history:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"**👤 Vous:** {msg['message']}")
                else:
                    st.markdown(f"**🤖 Assistant:** {msg['message']}")
                st.markdown("---")
        else:
            st.info("Aucun message encore")
    else:
        st.warning("Aucune session active")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Projet ML - Chatbot Émotionnel "
   
    "</div>",
    unsafe_allow_html=True
)
