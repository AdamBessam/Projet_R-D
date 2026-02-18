import os
import jwt
from datetime import datetime, timedelta

# Require explicit JWT secret for security
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise EnvironmentError(
        "Environment variable JWT_SECRET_KEY must be set. Do not use default secrets in production."
    )

ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 1


def create_jwt(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if "sub" not in payload or "role" not in payload:
            raise Exception("Invalid token payload")

        return payload

    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
