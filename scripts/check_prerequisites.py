"""
Script de vérification des prérequis avant installation
Usage: python scripts/check_prerequisites.py
"""

import sys
import subprocess
import platform

def check_python_version():
    """Vérifier la version de Python"""
    print("🔍 Vérification de Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 11:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} détecté")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} détecté")
        print(f"   ⚠️  Python 3.11+ requis")
        return False


def check_pip():
    """Vérifier que pip est installé"""
    print("\n🔍 Vérification de pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ pip détecté : {result.stdout.strip()}")
            return True
        else:
            print("   ❌ pip non trouvé")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors de la vérification de pip : {e}")
        return False


def check_git():
    """Vérifier que Git est installé"""
    print("\n🔍 Vérification de Git...")
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"   ✅ Git détecté : {result.stdout.strip()}")
            return True
        else:
            print("   ⚠️  Git non trouvé (optionnel pour cloner le repo)")
            return True  # Non bloquant
    except FileNotFoundError:
        print("   ⚠️  Git non trouvé (optionnel pour cloner le repo)")
        return True  # Non bloquant
    except Exception as e:
        print(f"   ⚠️  Erreur lors de la vérification de Git : {e}")
        return True  # Non bloquant


def check_mysql():
    """Vérifier que MySQL est installé (via mysql command)"""
    print("\n🔍 Vérification de MySQL...")
    
    # Vérifier si XAMPP est installé (Windows)
    if platform.system() == "Windows":
        import os
        xampp_paths = [
            r"C:\xampp\mysql\bin\mysql.exe",
            r"C:\Program Files\xampp\mysql\bin\mysql.exe",
        ]
        
        xampp_found = False
        for path in xampp_paths:
            if os.path.exists(path):
                print(f"   ✅ XAMPP MySQL détecté : {path}")
                xampp_found = True
                break
        
        if not xampp_found:
            print("   ⚠️  XAMPP non détecté dans les chemins standards")
            print("   💡 Assurez-vous que XAMPP est installé et MySQL est démarré")
    else:
        # Linux/Mac
        try:
            result = subprocess.run(
                ["mysql", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"   ✅ MySQL détecté : {result.stdout.strip()}")
            else:
                print("   ⚠️  MySQL non détecté")
        except FileNotFoundError:
            print("   ⚠️  MySQL non détecté")
        except Exception as e:
            print(f"   ⚠️  Erreur lors de la vérification de MySQL : {e}")
    
    return True  # Non bloquant


def check_disk_space():
    """Vérifier l'espace disque disponible"""
    print("\n🔍 Vérification de l'espace disque...")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        
        free_gb = free / (1024 ** 3)
        
        if free_gb >= 2:
            print(f"   ✅ Espace libre : {free_gb:.2f} GB")
            return True
        else:
            print(f"   ⚠️  Espace libre faible : {free_gb:.2f} GB")
            print(f"   💡 Au moins 2 GB recommandé")
            return False
    except Exception as e:
        print(f"   ⚠️  Impossible de vérifier l'espace disque : {e}")
        return True  # Non bloquant


def check_internet_connection():
    """Vérifier la connexion Internet"""
    print("\n🔍 Vérification de la connexion Internet...")
    try:
        import urllib.request
        urllib.request.urlopen('https://pypi.org', timeout=5)
        print("   ✅ Connexion Internet OK")
        return True
    except Exception:
        print("   ⚠️  Pas de connexion Internet détectée")
        print("   💡 Une connexion est nécessaire pour installer les dépendances")
        return False


def check_venv_support():
    """Vérifier le support des environnements virtuels"""
    print("\n🔍 Vérification du support venv...")
    try:
        import venv
        print("   ✅ Module venv disponible")
        return True
    except ImportError:
        print("   ❌ Module venv non disponible")
        print("   💡 Installez python3-venv sur votre système")
        return False


def main():
    print("=" * 70)
    print("🔧 VÉRIFICATION DES PRÉREQUIS - RAG Legal Project")
    print("=" * 70)
    
    checks = []
    
    # Vérifications critiques
    checks.append(("Python 3.11+", check_python_version()))
    checks.append(("pip", check_pip()))
    checks.append(("venv support", check_venv_support()))
    checks.append(("Connexion Internet", check_internet_connection()))
    checks.append(("Espace disque", check_disk_space()))
    
    # Vérifications optionnelles
    check_git()
    check_mysql()
    
    # Résumé
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES VÉRIFICATIONS")
    print("=" * 70)
    
    critical_passed = all([check[1] for check in checks])
    
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
    
    print("\n" + "=" * 70)
    
    if critical_passed:
        print("✅ SYSTÈME PRÊT POUR L'INSTALLATION !")
        print("\nÉtapes suivantes :")
        print("  1. Démarrer MySQL dans XAMPP Control Panel")
        print("  2. Créer l'environnement virtuel :")
        print("     python -m venv .venv")
        print("  3. Activer l'environnement :")
        print("     .venv\\Scripts\\Activate.ps1  (Windows)")
        print("     source .venv/bin/activate    (Linux/Mac)")
        print("  4. Installer les dépendances :")
        print("     pip install -r requirements.txt")
        print("  5. Configurer la base de données :")
        print("     python scripts/setup_database.py")
        print("     python scripts/seed_users.py")
        print("  6. Lancer l'application :")
        print("     streamlit run src/app.py")
        print("\n📖 Guide complet : INSTALLATION.md")
        return 0
    else:
        print("❌ PRÉREQUIS MANQUANTS")
        print("\nVeuillez installer les composants manquants avant de continuer.")
        print("\n📖 Consultez INSTALLATION.md pour les instructions détaillées")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
