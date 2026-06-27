# src/database.py
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict

# Importamos nuestro patrón Singleton
from patterns.singleton import SingletonMeta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatDatabase(metaclass=SingletonMeta):
    """
    Gestor de base de datos SQLite que implementa el patrón Singleton.
    Maneja la persistencia del historial de conversaciones por ID de sesión.
    """
    def __init__(self):
        # Aseguramos que la BD se guarde en la carpeta 'data' en la raíz del proyecto
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_path = self.base_dir / "data" / "chat_history.db"
        self._init_db()

    def _init_db(self):
        """Inicializa la conexión y crea la tabla si no existe."""
        try:
            # check_same_thread=False permite que Streamlit interactúe sin problemas
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.conn.cursor()
            
            # Tabla para guardar cada mensaje asociado a una sesión
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
            logging.info("Base de datos SQLite inicializada correctamente.")
        except Exception as e:
            logging.error(f"Error al inicializar la base de datos: {e}")

    def save_message(self, session_id: str, role: str, content: str):
        """Guarda un mensaje individual (del usuario o del bot) en el historial."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        self.conn.commit()

    def get_recent_history(self, session_id: str, limit: int) -> List[Dict]:
        """
        Recupera los últimos 'limit' mensajes de una sesión específica.
        Cumple el requisito de 'tener en cuenta los N mensajes anteriores'.
        """
        cursor = self.conn.cursor()
        # Traemos los más recientes primero
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        
        # Los invertimos para devolverlos en orden cronológico normal (el más antiguo primero)
        rows.reverse()
        return [{"role": row[0], "content": row[1]} for row in rows]

# ==========================================
# Ejecución para prueba local
# ==========================================
if __name__ == "__main__":
    # Prueba rápida para confirmar que funciona
    db = ChatDatabase()
    db.save_message("sesion_prueba_123", "user", "Hola, ¿qué tarjetas tienes?")
    db.save_message("sesion_prueba_123", "assistant", "Tenemos la tarjeta Aqua y la Black.")
    
    historial = db.get_recent_history("sesion_prueba_123", limit=5)
    print("\n--- Historial Recuperado ---")
    for msg in historial:
        print(f"{msg['role'].upper()}: {msg['content']}")