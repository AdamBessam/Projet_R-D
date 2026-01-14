from users import USERS_DB


def authenticate_user(username: str, password: str):
    """
    Vérifie les identifiants utilisateur.
    Retourne le rôle si authentification réussie.
    """
    user = USERS_DB.get(username)

    if not user:
        return None

    if user["password"] != password:
        return None

    return user["role"]
