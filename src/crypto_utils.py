from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import os
import base64

class CryptoUtils:
    def __init__(self, key=None):
        self.key = key if key else os.urandom(32)
        
    def get_key(self):
        return self.key
    
    def set_key(self, key):
        self.key = key

    def encrypt(self, message: bytes) -> tuple:
        iv = os.urandom(16)
        
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message) + padder.finalize()
        
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        h = hmac.HMAC(self.key, hashes.SHA256())
        h.update(ciphertext)
        signature = h.finalize()
        
        return (ciphertext, signature, iv)

    def decrypt(self, ciphertext: bytes, signature: bytes, iv: bytes) -> bytes:
        h = hmac.HMAC(self.key, hashes.SHA256())
        h.update(ciphertext)
        try:
            h.verify(signature)
        except Exception as e:
            raise ValueError("Message authentication failed")
            
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
