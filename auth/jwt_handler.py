"""JWT-Handler: Erstellt, signiert und verifiziert Access- und Refresh-Tokens."""

from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from config import settings

TokenType = Literal["access", "refresh"]


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_token(subject: str, token_type: TokenType) -> str:
    """Erstellt ein signiertes JWT für den angegebenen Nutzer."""
    if token_type == "access":
        expire = _now_utc() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = _now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "sub": subject,
        "type": token_type,
        "iat": _now_utc(),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: TokenType) -> dict:
    """
    Dekodiert und validiert ein JWT.
    Wirft ValueError bei ungültigem oder abgelaufenem Token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except ExpiredSignatureError as exc:
        raise ValueError("Token ist abgelaufen.") from exc
    except InvalidTokenError as exc:
        raise ValueError(f"Ungültiges Token: {exc}") from exc

    if payload.get("type") != expected_type:
        raise ValueError(f"Falscher Token-Typ: erwartet '{expected_type}'.")

    return payload
