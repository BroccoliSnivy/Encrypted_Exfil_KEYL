"""
server.py
----------
Server side of a one-way encrypted communication system.
- Uses RSA to securely receive a Fernet session key from client.
- Then uses that Fernet key to decrypt all further messages.
"""

import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

# -----------------------------
# 1) Generate RSA key pair
# -----------------------------
# Server makes a public/private RSA keypair at runtime
rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
rsa_public_key = rsa_private_key.public_key()

# Serialize public key to bytes (PEM format) to send to client
rsa_public_pem = rsa_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# -----------------------------
# 2) Setup server socket
# -----------------------------
HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print(f"[*] Listening on {HOST}:{PORT}")
conn, addr = server.accept()
print(f"[*] Connection from {addr}")

# -----------------------------
# 3) Send public key to client
# -----------------------------
conn.sendall(rsa_public_pem)
print("[*] Sent RSA public key to client.")

# -----------------------------
# 4) Receive encrypted Fernet key
# -----------------------------
encrypted_session_key = conn.recv(4096)
session_key = rsa_private_key.decrypt(
    encrypted_session_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
fernet = Fernet(session_key)
print("[*] Fernet session key established.")

# -----------------------------
# 5) Receive encrypted messages (one way)
# -----------------------------
try:
    while True:
        data = conn.recv(4096)
        if not data:
            break

        try:
            message = fernet.decrypt(data).decode()
            print("Client:", message)
        except Exception as e:
            print("[!] Decryption failed:", e)

except KeyboardInterrupt:
    print("\n[*] Stopped by user.")
finally:
    conn.close()
    server.close()
