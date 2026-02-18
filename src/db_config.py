import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """
    Crée et retourne une connexion à la base de données MySQL.
    
    Variables d'environnement requises :
    - MYSQL_HOST : Adresse du serveur MySQL (défaut: localhost)
    - MYSQL_PORT : Port MySQL (défaut: 3306)
    - MYSQL_DATABASE : Nom de la base de données
    - MYSQL_USER : Nom d'utilisateur MySQL
    - MYSQL_PASSWORD : Mot de passe MySQL
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            database=os.getenv("MYSQL_DATABASE", "rag_legal_db"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "")
        )
        
        if connection.is_connected():
            return connection
            
    except Error as e:
        print(f"Erreur de connexion MySQL : {e}")
        return None


def close_db_connection(connection):
    """Ferme proprement la connexion à la base de données."""
    if connection and connection.is_connected():
        connection.close()


def test_connection():
    """Teste la connexion à la base de données."""
    conn = get_db_connection()
    if conn:
        print("✅ Connexion MySQL réussie !")
        db_info = conn.get_server_info()
        print(f"Version MySQL : {db_info}")
        close_db_connection(conn)
        return True
    else:
        print("❌ Échec de connexion MySQL")
        return False


if __name__ == "__main__":
    test_connection()
