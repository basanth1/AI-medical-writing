"""
backend/db/user_store.py
JSON-file-based user store for self-registered users.
- Passwords are hashed with SHA-256 + per-user salt
- Admin accounts remain managed via .env (not stored here)
- Only "user" role accounts are created through sign-up
"""
from __future__ import annotations
import hashlib
import json
import os
import secrets
import threading
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

_STORE_DIR = os.path.join(os.path.dirname(__file__), "registered_users")
_STORE_FILE = os.path.join(_STORE_DIR, "users.json")
_lock = threading.Lock()


def _ensure_store() -> None:
    """Create the store directory and file if they don't exist."""
    os.makedirs(_STORE_DIR, exist_ok=True)
    if not os.path.isfile(_STORE_FILE):
        with open(_STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _read_store() -> Dict[str, Any]:
    """Read the user store from disk."""
    _ensure_store()
    try:
        with open(_STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _write_store(data: Dict[str, Any]) -> None:
    """Write the user store to disk."""
    _ensure_store()
    with open(_STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _hash_password(password: str, salt: str) -> str:
    """Hash a password with the given salt using SHA-256."""
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def user_exists(username: str) -> bool:
    """Check if a username is already registered."""
    with _lock:
        store = _read_store()
        return username.lower() in store


def register_user(
    username: str,
    password: str,
    full_name: str = "",
    email: str = "",
) -> Dict[str, Any]:
    """
    Register a new user. Returns the user record (without password hash).
    Raises ValueError if username already exists or is reserved.
    """
    uname = username.lower().strip()

    if not uname or not password:
        raise ValueError("Username and password are required")
    if len(uname) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

    with _lock:
        store = _read_store()

        if uname in store:
            raise ValueError("Username is already taken")

        salt = secrets.token_hex(16)
        pw_hash = _hash_password(password, salt)

        user_record = {
            "username": uname,
            "full_name": full_name.strip(),
            "email": email.strip().lower(),
            "role": "user",
            "salt": salt,
            "password_hash": pw_hash,
            "created_at": time.time(),
            "status": "active",
        }

        store[uname] = user_record
        _write_store(store)
        logger.info("New user registered: %s", uname)

    # Return a safe copy (no salt/hash)
    return {
        "username": uname,
        "full_name": user_record["full_name"],
        "email": user_record["email"],
        "role": "user",
        "status": "active",
    }


def verify_user(username: str, password: str) -> Optional[Dict[str, str]]:
    """
    Verify credentials for a registered user.
    Returns {"username": ..., "role": ...} on success, None on failure.
    """
    uname = username.lower().strip()

    with _lock:
        store = _read_store()
        user = store.get(uname)

    if not user:
        return None
    if user.get("status") != "active":
        return None

    pw_hash = _hash_password(password, user["salt"])
    if pw_hash != user["password_hash"]:
        return None

    return {"username": user["username"], "role": user["role"]}


def list_users() -> list:
    """List all registered users (without sensitive data)."""
    with _lock:
        store = _read_store()
    return [
        {
            "username": u["username"],
            "full_name": u.get("full_name", ""),
            "email": u.get("email", ""),
            "role": u["role"],
            "status": u.get("status", "active"),
            "created_at": u.get("created_at"),
        }
        for u in store.values()
    ]
