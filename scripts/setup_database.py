"""
Script pour créer la base de données et la table users directement depuis Python.
"""
import sys
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

print("🔧 Création de la base de données MySQL...\n")

try:
    # Connexion initiale sans spécifier de base (pour créer la base)
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "")
    )
    
    if connection.is_connected():
        print("✅ Connexion au serveur MySQL réussie")
        cursor = connection.cursor()
        
        db_name = os.getenv("MYSQL_DATABASE", "rag_legal_db")
        
        # 1. Créer la base de données
        print(f"\n📝 Création de la base de données '{db_name}'...")
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("   ✅ Base de données créée (ou déjà existante)")
        except Error as e:
            print(f"   ⚠️  {e}")
        
        # 2. Sélectionner la base
        cursor.execute(f"USE {db_name}")
        print(f"   ✅ Base de données '{db_name}' sélectionnée")
        
        # 3. Créer la table users
        print(f"\n📝 Création de la table 'users'...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('guest', 'employee', 'admin') NOT NULL DEFAULT 'guest',
            email VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_username (username),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_table_sql)
        print("   ✅ Table 'users' créée (ou déjà existante)")
        
        # 4. Afficher la structure de la table
        print(f"\n📋 Structure de la table 'users' :")
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"   - {col[0]:20} {col[1]:30} {col[2]}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "="*70)
        print("✅ Base de données et table créées avec succès !")
        print("="*70)
        print("\n📍 Prochaine étape :")
        print("   python scripts/seed_users.py")
        print()
        
except Error as e:
    print(f"\n❌ Erreur MySQL : {e}")
    print("\n💡 Vérifications :")
    print("   1. MySQL est-il démarré ? (XAMPP ou service Windows)")
    print("   2. Le mot de passe dans .env est-il correct ?")
    print("   3. L'utilisateur MySQL root existe-t-il ?")
    sys.exit(1)
