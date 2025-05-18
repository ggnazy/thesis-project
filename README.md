# Simple VPN Project

## TLS Certificate Generation

Before running the VPN system, you need to generate the required TLS certificates. Follow these steps:

1. Make sure OpenSSL is installed:
```bash
sudo apt update
sudo apt install openssl
```

2. Navigate to the project directory:
```bash
cd /path/to/vpn-project
```

3. Create the TLS configuration directory if it doesn't exist:
```bash
mkdir -p tls_config
```

4. Generate certificates using the following commands:

```bash
# Generate CA private key and certificate
openssl genrsa -out tls_config/ca.key 4096
openssl req -x509 -new -nodes \
    -key tls_config/ca.key \
    -sha256 -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=VPN-CA" \
    -out tls_config/ca.crt

# Generate server private key and CSR
openssl genrsa -out tls_config/server.key 4096
openssl req -new \
    -key tls_config/server.key \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    -out tls_config/server.csr

# Sign server certificate with CA
openssl x509 -req \
    -in tls_config/server.csr \
    -CA tls_config/ca.crt \
    -CAkey tls_config/ca.key \
    -CAcreateserial \
    -out tls_config/server.crt \
    -days 365 \
    -sha256

# Set proper permissions
chmod 600 tls_config/*.key
```

For convenience, you can also use the provided script:

````python
// filepath: /home/silvia/Documents/vpn-project/scripts/generate_certs.py
#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        exit(1)

def generate_certificates():
    # Create tls_config directory
    Path("tls_config").mkdir(exist_ok=True)
    
    # Generate CA key and certificate
    run_command("openssl genrsa -out tls_config/ca.key 4096")
    run_command("""
        openssl req -x509 -new -nodes \
        -key tls_config/ca.key \
        -sha256 -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=VPN-CA" \
        -out tls_config/ca.crt
    """)

    # Generate server key and CSR
    run_command("openssl genrsa -out tls_config/server.key 4096")
    run_command("""
        openssl req -new \
        -key tls_config/server.key \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        -out tls_config/server.csr
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
        -sha256
    """)

    # Set proper permissions
    run_command("chmod 600 tls_config/*.key")
    
    print("Certificates generated successfully!")

if __name__ == "__main__":
    generate_certificates()