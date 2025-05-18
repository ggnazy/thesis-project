import pytest
from src.crypto_utils import CryptoUtils

def test_encryption_decryption():
    crypto = CryptoUtils()
    message = b"Test message"
    
    # Encrypt
    ciphertext, signature, iv = crypto.encrypt(message)
    
    # Decrypt
    decrypted = crypto.decrypt(ciphertext, signature, iv)
    
    assert decrypted == message

def test_tampered_message():
    crypto = CryptoUtils()
    message = b"Test message"
    
    # Encrypt
    ciphertext, signature, iv = crypto.encrypt(message)
    
    # Tamper with ciphertext
    tampered = bytearray(ciphertext)
    tampered[0] ^= 1
    
    # Attempt to decrypt
    with pytest.raises(ValueError):
        crypto.decrypt(bytes(tampered), signature, iv)