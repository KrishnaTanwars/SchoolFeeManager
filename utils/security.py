"""
Security & Password Hashing utilities using PBKDF2-HMAC-SHA256.
"""

import hashlib
import os
import secrets

def hash_password(password: str) -> str:
    """Hashes a password with a randomly generated 16-byte salt using PBKDF2-HMAC-SHA256."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return salt.hex() + ":" + key.hex()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against the stored salt:hash string."""
    if not password or not hashed_password or ":" not in hashed_password:
        return False
    try:
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return secrets.compare_digest(key, new_key)
    except Exception:
        return False
