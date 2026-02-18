"""
Script de diagnostic pour identifier les problèmes MySQL.
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🔍 DIAGNOSTIC MYSQL")
print("="*70)
print()

# 1. Vérifier les variables d'environnement
print("📋 Configuration dans .env :")
print(f"   MYSQL_HOST: {os.getenv('MYSQL_HOST', 'NON DÉFINI')}")
print(f"   MYSQL_PORT: {os.getenv('MYSQL_PORT', 'NON DÉFINI')}")
print(f"   MYSQL_DATABASE: {os.getenv('MYSQL_DATABASE', 'NON DÉFINI')}")
print(f"   MYSQL_USER: {os.getenv('MYSQL_USER', 'NON DÉFINI')}")
print(f"   MYSQL_PASSWORD: {'***' if os.getenv('MYSQL_PASSWORD') else 'NON DÉFINI'}")
print()

# 2. Vérifier si MySQL est accessible
print("🔌 Test de connexion MySQL...")
print()

import mysql.connector
from mysql.connector import Error

# Test 1 : Avec mot de passe
try:
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "")
    )
    
    if connection.is_connected():
        print("✅ Connexion réussie avec le mot de passe du .env")
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   Version MySQL : {version[0]}")
        cursor.close()
        connection.close()
        
        print("\n🎉 MySQL est configuré correctement !")
        print("\n📍 Prochaine étape :")
        print("   python scripts/setup_database.py")
        exit(0)
        
except Error as e:
    print(f"❌ Échec avec mot de passe : {e}")
    print()

# Test 2 : Sans mot de passe
print("🔄 Test sans mot de passe...")
try:
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=""
    )
    
    if connection.is_connected():
        print("✅ Connexion réussie SANS mot de passe")
        print("\n💡 Solution : Mettez un mot de passe vide dans .env :")
        print("   MYSQL_PASSWORD=")
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"\n   Version MySQL : {version[0]}")
        cursor.close()
        connection.close()
        exit(0)
        
except Error as e:
    print(f"❌ Échec sans mot de passe : {e}")
    print()

# Si on arrive ici, aucune connexion n'a fonctionné
print("\n" + "="*70)
print("❌ IMPOSSIBLE DE SE CONNECTER À MYSQL")
print("="*70)
print()
print("💡 Solutions possibles :")
print()
print("1️⃣  Vérifier que MySQL est démarré")
print("    • Si XAMPP : Ouvrir le panneau et démarrer MySQL")
print("    • Si service Windows :")
print("      net start MySQL80")
print()
print("2️⃣  Vérifier le mot de passe MySQL")
print("    • Par défaut XAMPP : pas de mot de passe (vide)")
print("    • Par défaut MySQL standard : définir un mot de passe à l'installation")
print()
print("3️⃣  Tester manuellement avec mysql.exe (si dans le PATH)")
print("    mysql -u root -p")
print()
print("4️⃣  Options de mot de passe courants à essayer dans .env :")
print("    MYSQL_PASSWORD=          (vide)")
print("    MYSQL_PASSWORD=root")
print("    MYSQL_PASSWORD=admin")
print("    MYSQL_PASSWORD=password")
print()
print("5️⃣  Si vous utilisez XAMPP/WAMP :")
print("    • Ouvrir phpMyAdmin : http://localhost/phpmyadmin")
print("    • Si ça fonctionne, le mot de passe est probablement vide")
print()
