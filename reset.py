from datetime import datetime
from db import get_connection

def reset_metrics_if_needed():
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.now()

        
        cursor.execute("SELECT name_question, last_time_updated FROM bot_questions")
        rows = cursor.fetchall()

        for name_question, last_update in rows:
            updates = []

            if last_update.year != now.year:
               
                updates = [
                    "X_ANO = 0",
                    "X_MES = 0",
                    "X_DIA = 0"
                ]
            elif last_update.month != now.month:
                
                updates = [
                    "X_MES = 0",
                    "X_DIA = 0"
                ]
            elif last_update.day != now.day:
                
                updates = [
                    "X_DIA = 0"
                ]

            if updates:
                update_stmt = f"""
                UPDATE bot_questions
                SET {', '.join(updates)}
                WHERE name_question = %s
                """
                cursor.execute(update_stmt, (name_question,))

        conn.commit()

    except Exception as e:
        print(f"Erro ao resetar métricas: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
