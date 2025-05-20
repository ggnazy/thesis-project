import socket
import ssl
from crypto_utils import CryptoUtils
import base64
import logging
import sys

class VPNClient:
    def __init__(self, host='192.168.100.10', port=4433):
        self.host = host
        self.port = port
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/client.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations(cafile='tls_config/ca.crt')
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.check_hostname = False  # Since we're using IP address
        
        test_key = b'0XvWRTQJhNvz92USNoD+E/1a0B9Pij32SlOay0iQiSI='
        self.crypto = CryptoUtils(base64.b64decode(test_key))
        
        self.logger.debug("SSL Context initialized with CA certificate")
    
    def connect(self):
        try:
            self.logger.debug(f"Attempting to connect to {self.host}:{self.port}")
            sock = socket.create_connection((self.host, self.port), timeout=5)
            return self.context.wrap_socket(sock, server_hostname=self.host)
        except ConnectionRefusedError:
            self.logger.error(f"Connection refused to {self.host}:{self.port}. Is the server running?")
            raise
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise
        
    def send_message(self, message: str):
        try:
            with self.connect() as ssock:
                ciphertext, signature, iv = self.crypto.encrypt(message.encode())
                
                full_message = ciphertext + signature + iv
                
                ssock.send(full_message)
                
                response = ssock.recv(1024)
                print(f"Server response: {response.decode()}")
                
        except Exception as e:
            print(f"Error sending message: {e}")

if __name__ == "__main__":
    client = VPNClient()
    while True:
        message = input("Enter message (or 'quit' to exit): ")
        if message.lower() == 'quit':
            break
        client.send_message(message)
