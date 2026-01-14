# Base utilisateurs simulée (prototype)
# ⚠️ En production : base de données / LDAP / IdP

USERS_DB = {
    "alice": {
        "password": "alice123",
        "role": "guest"
    },
    "bob": {
        "password": "bob123",
        "role": "employee"
    },
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}
