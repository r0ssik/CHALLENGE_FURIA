from db import get_connection
from datetime import datetime

def update_question_metrics(name_question):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Nova query com INSERT ON DUPLICATE
        update_query = """
        INSERT INTO bot_questions (name_question, X_DIA, X_MES, X_ANO, X_GERAL, last_time_updated)
        VALUES (%s, 1, 1, 1, 1, %s)
        ON DUPLICATE KEY UPDATE
            X_DIA = X_DIA + 1,
            X_MES = X_MES + 1,
            X_ANO = X_ANO + 1,
            X_GERAL = X_GERAL + 1,
            last_time_updated = VALUES(last_time_updated);
        """

        now = datetime.now()
        cursor.execute(update_query, (name_question, now))

        # Inserir um evento na tabela de histórico
        insert_query = """
        INSERT INTO bot_questions_slave (name_question, data)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (name_question, now))

        conn.commit()

    except Exception as e:
        print(f"Erro ao atualizar métricas: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
