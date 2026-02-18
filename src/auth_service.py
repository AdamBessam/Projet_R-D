from db_config import get_db_connection, close_db_connection
import bcrypt
from datetime import datetime


def authenticate_user(username: str, password: str):
    """
    Vérifie les identifiants utilisateur dans la base MySQL.
    Retourne le rôle si authentification réussie, None sinon.
    
    Utilise bcrypt pour vérifier le mot de passe haché.
    Met à jour le timestamp de dernière connexion en cas de succès.
    """
    connection = get_db_connection()
    
    if not connection:
        print("❌ Erreur de connexion à la base de données")
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Récupérer l'utilisateur par username
        query = """
            SELECT id, username, password_hash, role, is_active
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        # Vérifier si l'utilisateur existe
        if not user:
            cursor.close()
            close_db_connection(connection)
            return None
        
        # Vérifier si le compte est actif
        if not user.get("is_active", True):
            print(f"⚠️ Compte '{username}' désactivé")
            cursor.close()
            close_db_connection(connection)
            return None
        
        # Vérifier le mot de passe avec bcrypt
        password_hash = user.get("password_hash", "")
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                # Authentification réussie, mettre à jour last_login
                update_query = """
                    UPDATE users
                    SET last_login = %s
                    WHERE id = %s
                """
                cursor.execute(update_query, (datetime.now(), user["id"]))
                connection.commit()
                
                cursor.close()
                close_db_connection(connection)
                return user["role"]
            else:
                cursor.close()
                close_db_connection(connection)
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du mot de passe : {e}")
            cursor.close()
            close_db_connection(connection)
            return None
    
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification : {e}")
        if connection:
            close_db_connection(connection)
        return None


def get_user_info(username: str):
    """
    Récupère les informations d'un utilisateur (sans le mot de passe).
    Retourne un dictionnaire avec les infos ou None si non trouvé.
    """
    connection = get_db_connection()
    
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = """
            SELECT id, username, role, email, created_at, last_login, is_active
            FROM users
            WHERE username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        cursor.close()
        close_db_connection(connection)
        
        return user
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des infos utilisateur : {e}")
        if connection:
            close_db_connection(connection)
        return None
