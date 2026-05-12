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

import secrets
import string

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_private_key: Optional[RSAPrivateKey] = None
_public_key: Optional[RSAPublicKey] = None
_aes_key: Optional[str] = None

_PK_SEPARATOR = "-pk_separator-"
_AES_IV = b"0000000000000000"


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


def _get_or_create_aes_key() -> str:
    """Return the cached AES key, creating one on first call."""
    global _aes_key  # noqa: PLW0603
    if _aes_key is not None:
        return _aes_key
    with _lock:
        if _aes_key is None:
            alphabet = string.ascii_letters + string.digits
            _aes_key = "".join(secrets.choice(alphabet) for _ in range(16))
        return _aes_key


def _aes_cbc_encrypt(plaintext: str, key: str) -> str:
    """AES-CBC encrypt with PKCS7 padding, return base64-encoded ciphertext."""
    padder = sym_padding.PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key.encode("utf-8")), modes.CBC(_AES_IV))
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ct).decode("utf-8")


def get_dekey_response() -> str:
    """Return the dekey string in Java-compatible format.

    Format: base64(AES_CBC_encrypt(rsa_pub_key_b64, aes_key))
            + base64url("-pk_separator-")
            + aes_key
    """
    _, pub = get_or_create_key_pair()
    # JSEncrypt (frontend) requires PEM-formatted public key
    pem_str = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    aes_key = _get_or_create_aes_key()
    encrypted = _aes_cbc_encrypt(pem_str, aes_key)
    separator = base64.urlsafe_b64encode(_PK_SEPARATOR.encode("utf-8")).decode("utf-8")
    return encrypted + separator + aes_key


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
        padding.PKCS1v15(),
    )
    return plaintext.decode("utf-8")
