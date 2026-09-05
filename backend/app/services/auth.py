"""SQLite-backed user authentication for ProjectX-Ray."""
import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("PROJECTXRAY_DB_PATH", "projectxray.db"))


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password_hash TEXT NOT NULL, salt TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    conn.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, target_users TEXT NOT NULL, technologies TEXT NOT NULL, analysis_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn


def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return digest, salt


def register_user(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if len(email) < 5 or "@" not in email:
        return False, "Enter a valid email address."
    if len(password) < 6:
        return False, "Password must contain at least 6 characters."
    conn = _db()
    try:
        if conn.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
            return False, "An account with this email already exists."
        password_hash, salt = _hash_password(password)
        conn.execute("INSERT INTO users(email,password_hash,salt) VALUES(?,?,?)", (email, password_hash, salt))
        conn.commit()
        return True, "Account created successfully."
    finally:
        conn.close()


def authenticate(email: str, password: str) -> bool:
    email = email.strip().lower()
    conn = _db()
    try:
        row = conn.execute("SELECT password_hash,salt FROM users WHERE email=?", (email,)).fetchone()
        if not row:
            return False
        digest, _ = _hash_password(password, row["salt"])
        return hmac.compare_digest(digest, row["password_hash"])
    finally:
        conn.close()


def ensure_demo_user() -> None:
    if not authenticate("demo@projectxray.app", "projectxray123"):
        register_user("demo@projectxray.app", "projectxray123")


def save_project(email: str, project: dict, analysis: dict) -> None:
    import json
    conn = _db()
    try:
        conn.execute("INSERT INTO projects(email,title,description,target_users,technologies,analysis_json) VALUES(?,?,?,?,?,?)", (email.strip().lower(), project["title"], project["description"], project["target_users"], json.dumps(project.get("technologies", [])), json.dumps(analysis)))
        conn.commit()
    finally:
        conn.close()


def get_projects(email: str) -> list[dict]:
    import json
    conn = _db()
    try:
        rows = conn.execute("SELECT id,title,description,target_users,technologies,analysis_json,created_at FROM projects WHERE email=? ORDER BY id DESC", (email.strip().lower(),)).fetchall()
        return [{"id": r["id"], "title": r["title"], "description": r["description"], "target_users": r["target_users"], "technologies": json.loads(r["technologies"]), "analysis": json.loads(r["analysis_json"]), "created_at": r["created_at"]} for r in rows]
    finally:
        conn.close()
