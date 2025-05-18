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
    
    # Generate CA key and certificate
    print("Generating CA key and certificate...")
    run_command("openssl genrsa -out tls_config/ca.key 4096")
    run_command("""
        openssl req -x509 -new -nodes \
        -key tls_config/ca.key \
        -sha256 -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=VPN-CA" \
        -out tls_config/ca.crt
    """)

    # Generate server key and CSR
    print("Generating server key and CSR...")
    run_command("openssl genrsa -out tls_config/server.key 4096")
    run_command("""
        openssl req -new \
        -key tls_config/server.key \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        -out tls_config/server.csr
    """)

    # Sign server certificate
    print("Signing server certificate with CA...")
    run_command("""
        openssl x509 -req \
        -in tls_config/server.csr \
        -CA tls_config/ca.crt \
        -CAkey tls_config/ca.key \
        -CAcreateserial \
        -out tls_config/server.crt \
        -days 365 \
        -sha256
    """)

    # Set proper permissions
    print("Setting proper permissions...")
    run_command("chmod 600 tls_config/*.key")
    
    # Clean up CSR file
    print("Cleaning up...")
    run_command("rm tls_config/server.csr")
    
    print("\nCertificates generated successfully!")
    print("\nGenerated files:")
    print("- tls_config/ca.key (CA private key)")
    print("- tls_config/ca.crt (CA certificate)")
    print("- tls_config/server.key (Server private key)")
    print("- tls_config/server.crt (Server certificate)")

if __name__ == "__main__":
    generate_certificates()