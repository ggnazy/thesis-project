from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os

class CryptoUtils:
    def __init__(self, key=None):
        # Generate or use provided 32-byte key for AES-256
        self.key = key if key else os.urandom(32)
        # Generate IV for AES-CBC mode
        self.iv = os.urandom(16)

    def encrypt(self, message: bytes) -> tuple:
        # Pad the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message) + padder.finalize()
        
        # Encrypt with AES-CBC
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Generate HMAC
        h = hmac.HMAC(self.key, hashes.SHA256())
        h.update(ciphertext)
        signature = h.finalize()
        
        return (ciphertext, signature, self.iv)

    def decrypt(self, ciphertext: bytes, signature: bytes, iv: bytes) -> bytes:
        # Verify HMAC
        h = hmac.HMAC(self.key, hashes.SHA256())
        h.update(ciphertext)
        try:
            h.verify(signature)
        except Exception as e:
            raise ValueError("Message authentication failed")
            
        # Decrypt with AES-CBC
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the message
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data