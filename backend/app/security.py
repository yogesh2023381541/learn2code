import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from .config import settings

def hash_password(password: str) -> str:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return bcrypt.hashpw(digest, bcrypt.gensalt()).decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return bcrypt.checkpw(digest, password_hash.encode("ascii"))


def create_access_token(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode(
        {"sub": str(user_id), "typ": "access", "exp": expires},
        settings.jwt_secret,
        algorithm="HS256",
    )


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    token_id = secrets.token_urlsafe(24)
    expires = datetime.now(UTC) + timedelta(days=settings.refresh_token_days)
    token = jwt.encode(
        {"sub": str(user_id), "jti": token_id, "typ": "refresh", "exp": expires},
        settings.jwt_secret,
        algorithm="HS256",
    )
    return token, token_id, expires


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str, expected_type: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        if payload.get("typ") != expected_type:
            raise ValueError("Invalid token type")
        if payload.get("sub") is None:
            raise ValueError("Token subject is missing")
        return payload
    except (JWTError, TypeError, ValueError) as error:
        raise ValueError("Invalid token") from error
