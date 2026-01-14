ROLE_TO_ACCESS = {
    "guest": "public",
    "employee": "internal",
    "admin": "confidential"
}


def get_access_level_from_role(role: str) -> str:
    return ROLE_TO_ACCESS.get(role, "public")
