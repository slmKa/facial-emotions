"""
Gestion de la base de données SQLite pour l'historique
"""

import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path="database/chatbot.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise les tables de la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Table emotions_log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emotions_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emotion TEXT NOT NULL,
                confidence REAL NOT NULL,
                mood_state TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Table messages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                emotion_context TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Table notifications
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notification_type TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_or_create_user(self, username):
        """Récupère ou crée un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
        else:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            user_id = cursor.lastrowid
            conn.commit()
        
        conn.close()
        return user_id
    
    def create_session(self, user_id):
        """Crée une nouvelle session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO sessions (user_id) VALUES (?)", (user_id,))
        session_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return session_id
    
    def log_emotion(self, session_id, emotion, confidence, mood_state):
        """Enregistre une émotion détectée"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO emotions_log (session_id, emotion, confidence, mood_state)
            VALUES (?, ?, ?, ?)
        """, (session_id, emotion, confidence, mood_state))
        
        conn.commit()
        conn.close()
    
    def log_message(self, session_id, role, message, emotion_context=None):
        """Enregistre un message (user ou bot)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (session_id, role, message, emotion_context)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, message, emotion_context))
        
        conn.commit()
        conn.close()
    
    def create_notification(self, user_id, notification_type, message):
        """Crée une notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (user_id, notification_type, message)
            VALUES (?, ?, ?)
        """, (user_id, notification_type, message))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id, limit=100):
        """Récupère les statistiques émotionnelles d'un utilisateur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.emotion, e.confidence, e.mood_state, e.timestamp
            FROM emotions_log e
            JOIN sessions s ON e.session_id = s.id
            WHERE s.user_id = ?
            ORDER BY e.timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_conversation_history(self, session_id):
        """Récupère l'historique de conversation d'une session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, message, emotion_context, timestamp
            FROM messages
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_unread_notifications(self, user_id):
        """Récupère les notifications non lues"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, notification_type, message, timestamp
            FROM notifications
            WHERE user_id = ? AND is_read = 0
            ORDER BY timestamp DESC
        """, (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def mark_notification_read(self, notification_id):
        """Marque une notification comme lue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = ?
        """, (notification_id,))
        
        conn.commit()
        conn.close()
