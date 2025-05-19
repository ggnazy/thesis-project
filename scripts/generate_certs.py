#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import tempfile

def run_command(command):
    """Execute shell command and handle errors"""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        exit(1)

def generate_certificates():
    """Generate all required certificates for VPN"""
    print("Starting certificate generation...")
    
    # Create tls_config directory
    Path("tls_config").mkdir(exist_ok=True)

    # Create CA config file
    ca_config = """
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = VPN-CA

[v3_ca]
basicConstraints = critical,CA:TRUE
keyUsage = critical,digitalSignature,keyCertSign,cRLSign
subjectKeyIdentifier = hash
"""
    # Create server config
    server_config = """
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = State
L = City
O = Organization
CN = 192.168.100.10

[v3_req]
basicConstraints = CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = IP:192.168.100.10
"""
    
    # Write configs to temporary files
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as ca_file:
        ca_file.write(ca_config)
        ca_config_path = ca_file.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as server_file:
        server_file.write(server_config)
        server_config_path = server_file.name

    try:
        # Generate CA key and certificate
        run_command(f"openssl req -x509 -new -nodes -keyout tls_config/ca.key -out tls_config/ca.crt -days 365 -config {ca_config_path}")

        # Generate server key
        run_command("openssl genrsa -out tls_config/server.key 4096")

        # Generate server CSR and certificate
        run_command(f"openssl req -new -key tls_config/server.key -out tls_config/server.csr -config {server_config_path}")
        run_command(f"""
            openssl x509 -req -in tls_config/server.csr -CA tls_config/ca.crt -CAkey tls_config/ca.key \
            -CAcreateserial -out tls_config/server.crt -days 365 -extfile {server_config_path} -extensions v3_req
        """)

        # Set proper permissions
        run_command("chmod 600 tls_config/*.key")
        run_command("chmod 644 tls_config/*.crt")
        
        print("Certificates generated successfully!")

    finally:
        # Clean up temporary files
        os.unlink(ca_config_path)
        os.unlink(server_config_path)

if __name__ == "__main__":
    generate_certificates()