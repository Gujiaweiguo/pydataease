"""Tests for MySQLBot AES encryption compatibility."""

from __future__ import annotations

import base64

from app.services.mysqlbot_service import _simple_aes_encrypt


def test_simple_aes_encrypt_decrypt_roundtrip() -> None:
    """Encrypt with our function, decrypt with the same algorithm — must match."""
    key = "test-key-that-is-32-bytes-long!!"
    iv = "test-iv-16-bytes!"
    plaintext = "my-secret-password"

    encrypted = _simple_aes_encrypt(plaintext, key, iv)

    # Must be valid base64
    raw = base64.b64decode(encrypted)
    assert len(raw) > 0
    assert len(raw) % 16 == 0  # AES block aligned

    # Decrypt manually to verify
    from cryptography.hazmat.primitives import padding as sym_padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    key_bytes = key[:32].ljust(32, "\x00").encode()
    iv_bytes = iv[:16].ljust(16, "\x00").encode()
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes))
    decryptor = cipher.decryptor()
    padded = decryptor.update(raw) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(padded) + unpadder.finalize()

    assert decrypted.decode() == plaintext


def test_simple_aes_encrypt_empty_string() -> None:
    """Encrypting an empty string should produce valid ciphertext (PKCS7 padding only)."""
    key = "any-key"
    iv = "any-iv-value-1234"
    encrypted = _simple_aes_encrypt("", key, iv)
    assert encrypted  # non-empty base64


def test_simple_aes_encrypt_produces_different_ciphertext() -> None:
    """Different keys produce different ciphertext."""
    plaintext = "same-input"
    iv = "fixed-iv-12345678"
    enc1 = _simple_aes_encrypt(plaintext, "key-one-12345678901234567890", iv)
    enc2 = _simple_aes_encrypt(plaintext, "key-two-12345678901234567890", iv)
    assert enc1 != enc2
