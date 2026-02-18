from users import USERS_DB
import bcrypt


def authenticate_user(username: str, password: str):
    """
    Vérifie les identifiants utilisateur.
    Retourne le rôle si authentification réussie.

    Supporte deux formats côté stockage :
    - mot de passe en clair (prototype)
    - mot de passe haché bcrypt (production)
    """
    user = USERS_DB.get(username)

    if not user:
        return None

    stored = user.get("password", "")

    # si le mot de passe stocké semble être un hash bcrypt
    if isinstance(stored, str) and stored.startswith("$2"):
        try:
            if bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8")):
                return user["role"]
            return None
        except Exception:
            return None

    # fallback : comparaison en clair (prototype)
    if stored != password:
        return None

    return user["role"]
