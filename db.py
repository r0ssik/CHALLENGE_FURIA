# db.py
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling

load_dotenv()  # <- ADICIONADO para carregar variáveis do .env

DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_SENHA = os.getenv("DB_SENHA")
DB_USER = os.getenv("DB_USER")

DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_SENHA,  # Mesmo vazio, tem que passar
    'database': DB_NAME
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=10,
    **DB_CONFIG
)

def get_connection():
    """Pega uma conexão da piscina."""
    return connection_pool.get_connection()

def close_all_connections():
    """Não precisa para mysql-connector, ele gerencia internamente."""
    pass
