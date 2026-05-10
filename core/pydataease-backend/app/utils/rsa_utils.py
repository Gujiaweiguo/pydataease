"""RSA key pair management and encrypt/decrypt utilities.

Generates an RSA-2048 key pair on first use (or loads from a PEM file
specified via the ``DE_RSA_PRIVATE_KEY_PATH`` environment variable).

All encryption uses OAEP padding with SHA-256 and MGF1, matching the
Java backend's RSA configuration.
"""

from __future__ import annotations

import base64
import logging
import os
import threading
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_private_key: Optional[RSAPrivateKey] = None
_public_key: Optional[RSAPublicKey] = None


def _load_private_key_from_file(path: str) -> RSAPrivateKey:
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def _generate_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return priv, priv.public_key()


def get_or_create_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    """Return the cached key pair, creating one on first call.

    If ``DE_RSA_PRIVATE_KEY_PATH`` is set, the private key is loaded from
    that PEM file instead of generating a new one.
    """
    global _private_key, _public_key  # noqa: PLW0603

    if _private_key is not None and _public_key is not None:
        return _private_key, _public_key

    with _lock:
        # Double-check after acquiring the lock.
        if _private_key is not None and _public_key is not None:
            return _private_key, _public_key

        pem_path = os.environ.get("DE_RSA_PRIVATE_KEY_PATH")
        if pem_path:
            logger.info("Loading RSA private key from %s", pem_path)
            priv = _load_private_key_from_file(pem_path)
            pub = priv.public_key()
        else:
            logger.info("Generating new RSA-2048 key pair")
            priv, pub = _generate_key_pair()

        _private_key = priv
        _public_key = pub
        return _private_key, _public_key


def get_public_key_pem() -> str:
    _, pub = get_or_create_key_pair()
    pem_bytes = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_bytes.decode("utf-8")


def decrypt_rsa(ciphertext_b64: str) -> str:
    """Decrypt a Base64-encoded RSA ciphertext using OAEP + SHA-256.

    Parameters
    ----------
    ciphertext_b64:
        Base64 string produced by the frontend after RSA-OAEP encryption.

    Returns
    -------
    str
        The decrypted plaintext.
    """
    priv, _ = get_or_create_key_pair()
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = priv.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return plaintext.decode("utf-8")
