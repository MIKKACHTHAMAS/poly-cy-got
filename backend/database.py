
import sqlite3

DB_PATH = "polycygot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            preferred_language TEXT DEFAULT 'en-IN',
            explanation_level TEXT DEFAULT 'simple',
            memory_consent BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_preferences(user_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM user_preferences WHERE user_id = ? AND memory_consent = 1",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def save_preferences(user_id: str, language: str, level: str, consent: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_preferences (user_id, preferred_language, explanation_level, memory_consent)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            preferred_language = excluded.preferred_language,
            explanation_level = excluded.explanation_level,
            memory_consent = excluded.memory_consent,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, language, level, consent))
    conn.commit()
    conn.close()

def delete_preferences(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_preferences WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
