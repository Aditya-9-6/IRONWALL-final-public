#!/bin/bash

# Define output files
KEY_FILE="key.pem"
CERT_FILE="cert.pem"

echo "🔐 Generating Self-Signed SSL Certificates for IronWall..."

# Generate a cached private key and a self-signed certificate valid for 365 days
# Nodes:
# -nodes: No password protection on the key (for automated server start)
# -newkey rsa:2048: Create a new 2048-bit RSA key
# -keyout: Save key to file
# -out: Save cert to file
# -subj: Avoids interactive prompt
openssl req -x509 -newkey rsa:2048 -keyout $KEY_FILE -out $CERT_FILE -days 365 -nodes -subj "/C=US/ST=State/L=City/O=IronWall/CN=localhost"

echo "✅ Done! Certificate ($CERT_FILE) and Key ($KEY_FILE) created."
echo "⚠️  OpSec Warning: These are self-signed. Browsers will warn you. For production, use Let's Encrypt."
