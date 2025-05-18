import socket
import ssl
from crypto_utils import CryptoUtils

class VPNClient:
    def __init__(self, host='localhost', port=4433):
        self.host = host
        self.port = port
        self.crypto = CryptoUtils()
        
        # SSL context setup
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('tls_config/ca.crt')
        
    def connect(self):
        sock = socket.create_connection((self.host, self.port))
        return self.context.wrap_socket(sock, server_hostname=self.host)
        
    def send_message(self, message: str):
        try:
            with self.connect() as ssock:
                # Encrypt message
                ciphertext, signature, iv = self.crypto.encrypt(message.encode())
                
                # Combine all components
                full_message = ciphertext + signature + iv
                
                # Send message
                ssock.send(full_message)
                
                # Get response
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