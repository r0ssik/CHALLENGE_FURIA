from db import get_connection

def criar_tabelas():
    comandos_sql = [
        """
        CREATE TABLE IF NOT EXISTS `bot_questions` (
            `name_question` VARCHAR(50) PRIMARY KEY,
            `X_DIA` INT(11) NOT NULL,
            `X_MES` INT(11) NOT NULL,
            `X_ANO` INT(11) NOT NULL,
            `X_GERAL` INT(11) NOT NULL,
            `last_time_updated` DATE DEFAULT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """,
        """
        CREATE TABLE IF NOT EXISTS `bot_questions_slave` (
            `id_question` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
            `name_question` VARCHAR(50) NOT NULL,
            `data` DATE NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
        """
    ]

    conn = get_connection()
    cursor = conn.cursor()

    for comando in comandos_sql:
        try:
            cursor.execute(comando)
            print("Tabela criada ou já existente.")
        except Exception as e:
            print(f"Erro ao criar tabela: {e}")

    conn.commit()
    cursor.close()
    conn.close()