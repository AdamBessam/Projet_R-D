"""
Script de vérification de la configuration MySQL.
Vérifie que tout est prêt pour utiliser l'authentification MySQL.
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db_config import get_db_connection, close_db_connection
from dotenv import load_dotenv

load_dotenv()


def check_env_variables():
    """Vérifie que les variables d'environnement MySQL sont définies."""
    print("🔍 Vérification des variables d'environnement...\n")
    
    required_vars = [
        "MYSQL_HOST",
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Masquer le mot de passe
            display_value = "***" if var == "MYSQL_PASSWORD" else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NON DÉFINI")
            missing.append(var)
    
    print()
    
    if missing:
        print(f"⚠️  Variables manquantes : {', '.join(missing)}")
        print("➡️  Configurez-les dans le fichier .env")
        return False
    
    print("✅ Toutes les variables d'environnement sont définies\n")
    return True


def check_mysql_connection():
    """Teste la connexion à MySQL."""
    print("🔌 Test de connexion MySQL...\n")
    
    connection = get_db_connection()
    
    if not connection:
        print("❌ Impossible de se connecter à MySQL")
        print("\n💡 Solutions possibles :")
        print("  1. Vérifier que MySQL est démarré (XAMPP ou service Windows)")
        print("  2. Vérifier les credentials dans .env")
        print("  3. Vérifier que la base de données existe")
        return False
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        print(f"  ✅ Connexion réussie !")
        print(f"  📊 Version MySQL : {version[0]}")
        
        cursor.close()
        close_db_connection(connection)
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if connection:
            close_db_connection(connection)
        return False


def check_database_exists():
    """Vérifie que la base de données existe."""
    print("🗄️  Vérification de la base de données...\n")
    
    connection = get_db_connection()
    
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Vérifier l'existence de la base
        db_name = os.getenv("MYSQL_DATABASE", "rag_legal_db")
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()
        
        if result:
            print(f"  ✅ Base de données '{db_name}' existe")
        else:
            print(f"  ❌ Base de données '{db_name}' n'existe pas")
            print(f"\n💡 Créez-la avec :")
            print(f"     mysql -u root -p < scripts/create_users_table.sql")
            cursor.close()
            close_db_connection(connection)
            return False
        
        cursor.close()
        close_db_connection(connection)
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if connection:
            close_db_connection(connection)
        return False


def check_users_table():
    """Vérifie que la table users existe."""
    print("👥 Vérification de la table users...\n")
    
    connection = get_db_connection()
    
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Vérifier l'existence de la table
        cursor.execute("SHOW TABLES LIKE 'users'")
        result = cursor.fetchone()
        
        if not result:
            print("  ❌ Table 'users' n'existe pas")
            print("\n💡 Créez-la avec :")
            print("     mysql -u root -p < scripts/create_users_table.sql")
            cursor.close()
            close_db_connection(connection)
            return False
        
        print("  ✅ Table 'users' existe")
        
        # Afficher la structure de la table
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        print("\n  📋 Structure de la table :")
        for col in columns:
            print(f"     - {col[0]:20} {col[1]:20} {col[2]}")
        
        cursor.close()
        close_db_connection(connection)
        print()
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if connection:
            close_db_connection(connection)
        return False


def check_default_users():
    """Vérifie que les utilisateurs par défaut existent."""
    print("👤 Vérification des utilisateurs par défaut...\n")
    
    connection = get_db_connection()
    
    if not connection:
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()["count"]
        
        if count == 0:
            print("  ⚠️  Aucun utilisateur dans la base")
            print("\n💡 Créez les utilisateurs par défaut avec :")
            print("     python scripts/seed_users.py")
            cursor.close()
            close_db_connection(connection)
            return False
        
        print(f"  ✅ {count} utilisateur(s) trouvé(s)")
        
        # Lister les utilisateurs
        cursor.execute("SELECT username, role, email, is_active FROM users")
        users = cursor.fetchall()
        
        print("\n  📊 Liste des utilisateurs :")
        for user in users:
            status = "✅ Actif" if user["is_active"] else "❌ Désactivé"
            print(f"     - {user['username']:10} | {user['role']:10} | {user['email']:30} | {status}")
        
        # Vérifier les utilisateurs par défaut
        default_users = ["alice", "bob", "admin"]
        existing_users = [u["username"] for u in users]
        
        missing = [u for u in default_users if u not in existing_users]
        
        if missing:
            print(f"\n  ⚠️  Utilisateurs manquants : {', '.join(missing)}")
            print("  💡 Exécutez : python scripts/seed_users.py")
        
        cursor.close()
        close_db_connection(connection)
        print()
        return count > 0
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        if connection:
            close_db_connection(connection)
        return False


def main():
    """Exécute toutes les vérifications."""
    print("=" * 70)
    print("🔍 VÉRIFICATION DE LA CONFIGURATION MYSQL")
    print("=" * 70)
    print()
    
    checks = [
        ("Variables d'environnement", check_env_variables),
        ("Connexion MySQL", check_mysql_connection),
        ("Base de données", check_database_exists),
        ("Table users", check_users_table),
        ("Utilisateurs par défaut", check_default_users)
    ]
    
    results = []
    
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    # Résumé
    print("=" * 70)
    print("📊 RÉSUMÉ")
    print("=" * 70)
    print()
    
    all_passed = True
    for name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"  {status:12} {name}")
        if not result:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 Tout est prêt ! Vous pouvez lancer l'application :")
        print("   streamlit run src/app.py")
    else:
        print("⚠️  Certaines vérifications ont échoué.")
        print("📖 Consultez MIGRATION_MYSQL.md pour plus d'aide.")
    
    print()


if __name__ == "__main__":
    main()
