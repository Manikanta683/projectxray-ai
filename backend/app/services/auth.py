"""Simple demo authentication helpers for ProjectX-Ray."""
from hashlib import sha256

_USERS = {
    "demo@projectxray.app": sha256("projectxray123".encode()).hexdigest(),
}


def authenticate(email: str, password: str) -> bool:
    return _USERS.get(email.strip().lower()) == sha256(password.encode()).hexdigest()
