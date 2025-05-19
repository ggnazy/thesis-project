#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

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
    
    # Generate CA key and certificate with proper extensions
    run_command("""
    openssl req -x509 -new -nodes \
        -keyout tls_config/ca.key \
        -out tls_config/ca.crt \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=VPN-CA" \
        -extensions v3_ca \
        -config <(echo "
            [ v3_ca ]
            basicConstraints=critical,CA:TRUE
            keyUsage=critical,digitalSignature,keyCertSign,cRLSign
            subjectKeyIdentifier=hash
        ")
    """)

    # Generate server key
    run_command("openssl genrsa -out tls_config/server.key 4096")

    # Generate server CSR
    run_command("""
    openssl req -new \
        -key tls_config/server.key \
        -out tls_config/server.csr \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.100.10"
    """)

    # Sign server certificate
    run_command("""
    openssl x509 -req \
        -in tls_config/server.csr \
        -CA tls_config/ca.crt \
        -CAkey tls_config/ca.key \
        -CAcreateserial \
        -out tls_config/server.crt \
        -days 365 \
        -extensions v3_req \
        -extfile <(echo "
            [ v3_req ]
            basicConstraints=CA:FALSE
            keyUsage=critical,digitalSignature,keyEncipherment
            extendedKeyUsage=serverAuth
            subjectAltName=IP:192.168.100.10
        ")
    """)

    # Set proper permissions
    run_command("chmod 600 tls_config/*.key")
    run_command("chmod 644 tls_config/*.crt")
    
    print("Certificates generated successfully!")

if __name__ == "__main__":
    generate_certificates()