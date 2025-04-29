
import schedule
import time
from db import get_connection
from datetime import datetime
import logging
import os


log_folder = 'logs'
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, 'cronjob.log')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def reset_metrics():
    now = datetime.now()
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        
        cursor.execute("UPDATE bot_questions SET X_DIA = 0")
        logging.info("X_DIA resetado com sucesso.")

       
        if now.day == 1:
            cursor.execute("UPDATE bot_questions SET X_MES = 0")
            logging.info("X_MES resetado com sucesso (primeiro dia do mês).")

        conn.commit()

    except Exception as e:
        logging.error(f"Erro ao executar cronjob: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


schedule.every().day.at("00:01").do(reset_metrics)

print("Agendador de tarefas iniciado...")


while True:
    schedule.run_pending()
    time.sleep(60)
