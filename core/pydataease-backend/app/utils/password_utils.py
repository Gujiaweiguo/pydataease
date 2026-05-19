"""Password hashing/verification and JWT secret derivation.

Uses ``bcrypt`` for secure password hashing and ``hashlib`` for
deterministic JWT secret derivation (matching the Java community
edition's MD5-based approach).
"""

from __future__ import annotations

import hashlib

import bcrypt


def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash of *plaintext*.

    The result is a UTF-8 encoded string suitable for storing in the
    database.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plaintext.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    """Check whether *plaintext* matches the bcrypt *hashed* value."""
    return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))


def derive_jwt_secret(password_hash: str) -> str:
    """Derive a deterministic JWT secret from a bcrypt password hash.

    Uses HMAC-SHA256 truncated to 32 hex chars.  Previous versions used
    MD5; tokens issued under the old scheme will need re-authentication.

    Parameters
    ----------
    password_hash:
        A bcrypt hash string (as returned by :func:`hash_password`).

    Returns
    -------
    str
        A 32-character hex string (SHA-256 digest, truncated).
    """
    return hashlib.sha256(password_hash.encode("utf-8")).hexdigest()[:32]
