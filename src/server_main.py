import socket
import ssl
import logging
from crypto_utils import CryptoUtils
from datetime import datetime

logging.basicConfig(
    filename='logs/vpn_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VPNServer:
    def __init__(self, host='0.0.0.0', port=4433):
        self.host = host
        self.port = port
        self.crypto = CryptoUtils()
        
        # SSL context setup
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(
            certfile='tls_config/server.crt',
            keyfile='tls_config/server.key'
        )
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)
            logging.info(f"Server started on {self.host}:{self.port}")
            
            with self.context.wrap_socket(sock, server_side=True) as ssock:
                while True:
                    try:
                        client_socket, addr = ssock.accept()
                        logging.info(f"Connection from {addr}")
                        self.handle_client(client_socket)
                    except Exception as e:
                        logging.error(f"Error handling client: {e}")

    def handle_client(self, client_socket):
        try:
            with client_socket:
                while True:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                        
                    ciphertext = data[:-48]
                    signature = data[-48:-16]
                    iv = data[-16:]
                    
                    try:
                        message = self.crypto.decrypt(ciphertext, signature, iv)
                        logging.info(f"Received message: {message.decode()}")
                        client_socket.send(b"Message received")
                    except Exception as e:
                        logging.error(f"Decryption error: {e}")
                        client_socket.send(b"Error processing message")
                        
        except Exception as e:
            logging.error(f"Connection error: {e}")

if __name__ == "__main__":
    server = VPNServer()
    server.start()