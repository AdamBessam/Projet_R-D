"""
Script pour insérer les utilisateurs de test dans la base MySQL.
"""
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_config import get_db_connection, close_db_connection
import bcrypt


def create_user(connection, username, password, role, email=None):
    """
    Crée un utilisateur dans la base de données avec mot de passe haché.
    """
    try:
        cursor = connection.cursor()
        
        # Hasher le mot de passe avec bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insérer l'utilisateur
        query = """
            INSERT INTO users (username, password_hash, role, email)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                role = VALUES(role),
                email = VALUES(email)
        """
        
        cursor.execute(query, (username, password_hash.decode('utf-8'), role, email))
        connection.commit()
        
        print(f"✅ Utilisateur '{username}' créé avec le rôle '{role}'")
        cursor.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur '{username}' : {e}")
        connection.rollback()


def seed_default_users():
    """
    Insère les utilisateurs par défaut dans la base de données.
    """
    connection = get_db_connection()
    
    if not connection:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    print("📝 Insertion des utilisateurs par défaut...\n")
    
    # Utilisateurs par défaut (mêmes que dans users.py)
    default_users = [
        {
            "username": "alice",
            "password": "alice123",
            "role": "guest",
            "email": "alice@example.com"
        },
        {
            "username": "bob",
            "password": "bob123",
            "role": "employee",
            "email": "bob@company.com"
        },
        {
            "username": "admin",
            "password": "admin123",
            "role": "admin",
            "email": "admin@company.com"
        }
    ]
    
    for user in default_users:
        create_user(
            connection,
            user["username"],
            user["password"],
            user["role"],
            user.get("email")
        )
    
    print("\n✅ Insertion terminée !")
    
    # Afficher les utilisateurs créés
    print("\n📊 Utilisateurs dans la base :")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, username, role, email, created_at FROM users")
    users = cursor.fetchall()
    
    for user in users:
        print(f"  - {user['username']:10} | Rôle: {user['role']:10} | Email: {user['email']}")
    
    cursor.close()
    close_db_connection(connection)


if __name__ == "__main__":
    seed_default_users()
