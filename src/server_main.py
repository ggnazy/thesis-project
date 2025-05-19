import socket
import ssl
import logging
import sys
import os
import base64
from crypto_utils import CryptoUtils

# Configure logging to both file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vpn_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)

class VPNServer:
    def __init__(self, host='0.0.0.0', port=4433):
        self.host = host
        self.port = port
        # Create crypto with fixed key for testing
        test_key = os.urandom(32)
        self.crypto = CryptoUtils(test_key)
        print(f"Using test key: {base64.b64encode(test_key).decode()}")
        
        self.logger = logging.getLogger(__name__)
        
        try:
            # SSL context setup
            self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.context.load_cert_chain(
                certfile='tls_config/server.crt',
                keyfile='tls_config/server.key'
            )
            self.logger.info("SSL Context initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SSL context: {e}")
            raise
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            self.logger.info(f"Server listening on {self.host}:{self.port}")
            
            with self.context.wrap_socket(sock, server_side=True) as ssock:
                while True:
                    try:
                        client_socket, addr = ssock.accept()
                        self.logger.info(f"Connection from {addr}")
                        self.handle_client(client_socket)
                    except Exception as e:
                        self.logger.error(f"Error handling client: {e}")

    def handle_client(self, client_socket):
        try:
            with client_socket:
                data = client_socket.recv(4096)
                if not data:
                    return
                    
                # Extract components
                ciphertext = data[:-48]  # Last 48 bytes are signature(32) + iv(16)
                signature = data[-48:-16]
                iv = data[-16:]
                
                try:
                    message = self.crypto.decrypt(ciphertext, signature, iv)
                    self.logger.info(f"Received message: {message.decode()}")
                    client_socket.send(b"Message received successfully")
                except Exception as e:
                    self.logger.error(f"Decryption error: {e}")
                    client_socket.send(b"Error processing message")
                        
        except Exception as e:
            self.logger.error(f"Connection error: {e}")

if __name__ == "__main__":
    server = VPNServer()
    server.start()