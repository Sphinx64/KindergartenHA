"""
Einfache In-Memory-Nutzerverwaltung mit bcrypt-gehashten Passwörtern.
Für Produktion durch eine echte Datenbank ersetzen.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Format: { "username": "bcrypt-hash" }
# Passwort-Hash erzeugen: python -c "from users import pwd_context; print(pwd_context.hash('meinPasswort'))"
_USER_DB: dict[str, str] = {
    "admin": pwd_context.hash("change-me"),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_hash(username: str) -> str | None:
    """Gibt den gespeicherten Passwort-Hash zurück, oder None wenn Nutzer unbekannt."""
    return _USER_DB.get(username)


def authenticate_user(username: str, password: str) -> bool:
    """Gibt True zurück, wenn Nutzer existiert und Passwort korrekt ist."""
    hashed = get_user_hash(username)
    if hashed is None:
        # Timing-Angriff verhindern: trotzdem hashen
        pwd_context.hash(password)
        return False
    return verify_password(password, hashed)
