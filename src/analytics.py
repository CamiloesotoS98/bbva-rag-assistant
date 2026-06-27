# src/analytics.py
import sqlite3
from pathlib import Path

class ChatAnalytics:
    """
    Módulo de análisis de datos para extraer métricas 
    del historial conversacional del sistema RAG.
    """
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_path = self.base_dir / "data" / "chat_history.db"

    def generate_report(self):
        if not self.db_path.exists():
            print("❌ No se encontró la base de datos de historial.")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. Total de sesiones únicas
            cursor.execute("SELECT COUNT(DISTINCT session_id) FROM messages")
            total_sessions = cursor.fetchone()[0]

            # 2. Conteo de mensajes por rol
            cursor.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
            role_counts = dict(cursor.fetchall())
            total_messages = sum(role_counts.values())

            # 3. Extraer textos para calcular promedios de longitud
            cursor.execute("SELECT role, content FROM messages")
            messages = cursor.fetchall()
            
            user_words = [len(m[1].split()) for m in messages if m[0] == 'user']
            bot_words = [len(m[1].split()) for m in messages if m[0] == 'assistant']

            avg_user_words = sum(user_words) / len(user_words) if user_words else 0
            avg_bot_words = sum(bot_words) / len(bot_words) if bot_words else 0

            # 4. Imprimir el reporte en consola
            print("\n" + "="*50)
            print("📊 REPORTE DE ANALÍTICA DEL ASISTENTE RAG 📊")
            print("="*50)
            print(f"🔹 Total de sesiones únicas: {total_sessions}")
            print(f"🔹 Total de mensajes procesados: {total_messages}")
            print(f"   - Preguntas de usuarios: {role_counts.get('user', 0)}")
            print(f"   - Respuestas del asistente: {role_counts.get('assistant', 0)}")
            print("-" * 50)
            print("📈 MÉTRICAS DE INTERACCIÓN:")
            print(f"   - Promedio de palabras por pregunta: {avg_user_words:.1f}")
            print(f"   - Promedio de palabras por respuesta: {avg_bot_words:.1f}")
            print("="*50 + "\n")

            conn.close()

        except Exception as e:
            print(f"Error al generar analíticas: {e}")

if __name__ == "__main__":
    analytics = ChatAnalytics()
    analytics.generate_report()