#!/usr/bin/env python3
"""Utilitaire simple pour hacher un mot de passe avec bcrypt.

Usage:
    python scripts/hash_password.py mypassword

La sortie est le hash bcrypt (copier/coller dans `src/users.py`).
"""
import sys
import bcrypt


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/hash_password.py <password>")
        sys.exit(1)

    pw = sys.argv[1]
    print(hash_password(pw))


if __name__ == "__main__":
    main()
