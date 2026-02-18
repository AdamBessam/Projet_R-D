"""
Script pour ajouter un nouvel utilisateur à la base de données
Usage: python scripts/add_user.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from src.db_config import get_db_connection, close_db_connection

def add_user(username, password, role, email=None):
    """
    Ajoute un nouvel utilisateur à la base de données
    
    Args:
        username: Nom d'utilisateur (unique)
        password: Mot de passe en clair (sera hashé)
        role: 'guest', 'employee', ou 'admin'
        email: Email de l'utilisateur (optionnel)
    """
    connection = get_db_connection()
    
    if not connection:
        print("❌ Erreur de connexion à la base de données")
        return False
    
    try:
        cursor = connection.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"❌ L'utilisateur '{username}' existe déjà")
            cursor.close()
            close_db_connection(connection)
            return False
        
        # Hash du mot de passe avec bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insertion du nouvel utilisateur
        query = """
            INSERT INTO users (username, password_hash, role, email)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (username, password_hash.decode('utf-8'), role, email))
        connection.commit()
        
        print(f"✅ Utilisateur '{username}' créé avec succès !")
        print(f"   - Rôle: {role}")
        print(f"   - Email: {email or 'Non défini'}")
        
        # Afficher le niveau d'accès correspondant
        access_mapping = {
            'guest': 'public',
            'employee': 'internal',
            'admin': 'confidential'
        }
        print(f"   - Niveau d'accès: {access_mapping.get(role, 'unknown')}")
        
        cursor.close()
        close_db_connection(connection)
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur : {e}")
        if connection:
            close_db_connection(connection)
        return False


def interactive_add_user():
    """Mode interactif pour ajouter un utilisateur"""
    print("=" * 60)
    print("🔐 AJOUT D'UN NOUVEL UTILISATEUR")
    print("=" * 60)
    
    # Demander les informations
    username = input("\n👤 Nom d'utilisateur: ").strip()
    if not username:
        print("❌ Le nom d'utilisateur est obligatoire")
        return
    
    password = input("🔑 Mot de passe: ").strip()
    if not password:
        print("❌ Le mot de passe est obligatoire")
        return
    
    print("\n📋 Rôles disponibles:")
    print("  1. guest     → Accès aux documents publics uniquement")
    print("  2. employee  → Accès aux documents publics + internes")
    print("  3. admin     → Accès à TOUS les documents (public + internal + confidential)")
    
    role_choice = input("\n👥 Choisir un rôle (1-3): ").strip()
    role_mapping = {"1": "guest", "2": "employee", "3": "admin"}
    role = role_mapping.get(role_choice)
    
    if not role:
        print("❌ Choix invalide")
        return
    
    email = input("📧 Email (optionnel, appuyez sur Entrée pour ignorer): ").strip()
    if not email:
        email = None
    
    # Confirmation
    print(f"\n📝 Récapitulatif:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print(f"   Role: {role}")
    print(f"   Email: {email or 'Non défini'}")
    
    confirm = input("\n✅ Confirmer la création ? (o/n): ").strip().lower()
    
    if confirm == 'o' or confirm == 'oui':
        add_user(username, password, role, email)
    else:
        print("❌ Création annulée")


if __name__ == "__main__":
    # Si des arguments sont fournis, les utiliser directement
    if len(sys.argv) > 1:
        if len(sys.argv) < 4:
            print("Usage: python scripts/add_user.py <username> <password> <role> [email]")
            print("Roles: guest, employee, admin")
            print("\nOu lancez sans arguments pour le mode interactif")
            sys.exit(1)
        
        username = sys.argv[1]
        password = sys.argv[2]
        role = sys.argv[3]
        email = sys.argv[4] if len(sys.argv) > 4 else None
        
        if role not in ['guest', 'employee', 'admin']:
            print("❌ Rôle invalide. Utilisez: guest, employee, ou admin")
            sys.exit(1)
        
        add_user(username, password, role, email)
    else:
        # Mode interactif
        interactive_add_user()
