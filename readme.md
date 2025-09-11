# 🔐 Keyl Enc — Encrypted Communication System

A compact Python project that demonstrates a **one-way encrypted communication channel** using **RSA** (for key exchange) and **Fernet** (for symmetric encryption).  
Includes a server with a Rich-powered terminal UI (banner, instructions, live tables, build output) and tools to build a standalone client executable.

> **Status:** Prototype / demo — for learning, testing and authorized uses only.

---

## 🔎 Quick summary
- Server generates an RSA keypair and sends the public key to a client.  
- Client generates a Fernet session key, encrypts it with the server RSA public key, and sends it back.  
- All subsequent messages are encrypted using Fernet and decrypted by the server.  
- Server displays messages in a live Rich table and logs them with timestamps.

---

## Project layout
```

.
├── server.py        # Main server: banner -> instruction -> (optional) build -> start listening
├── keyl\_enc.py      # Client-side script (edit HOST and PORT here before building)
├── build.py         # Standalone builder (build for linux or windows via Wine)
├── requirements.txt # Optional: dependency list
├── received\_messages.txt  # Generated at runtime: decrypted messages
└── dist/            # PyInstaller output (after building client)

````

---

## Requirements
- Python 3.8+  
- Recommended packages:
```bash
pip install cryptography rich pynput pyinstaller
````

**Notes**

* `cryptography` — RSA key ops and Fernet symmetric crypto
* `rich` — terminal UI (banners, panels, live displays)
* `pynput` — (optional) used by the client for capturing input (if implemented)
* `pyinstaller` — used to package `keyl_enc.py` into a single-file executable
* On Linux, to build a Windows `.exe` you can use `wine` + `pyinstaller` (see `build.py`)

You may prefer a `requirements.txt`:

```
cryptography
rich
pynput
pyinstaller
```

---

## Usage

### 1) Configure the client

Open `keyl_enc.py` and set these variables near the top:

```python
HOST = "x.x.x.x"   # server IP address
PORT = 4444       # port the server listens on
```

Make sure the values match the server's bind address and port.

---

### 2) Option A — Run server and build client interactively

Run the server; it will show the banner and an instruction panel, then ask whether to build the client:

```bash
python server.py -t <server-ip> -p <port>
```

Example:

```bash
python server.py -t 0.0.0.0 -p 4444
```

Flow:

1. Banner and instructions appear.
2. You will be prompted: `Proceed with build and start server? (y/n)`

   * If you type **y** the script will run PyInstaller to package `keyl_enc.py` (make sure HOST/PORT are already set inside it). The build output is shown in a live Rich panel.
   * After build completes, the server will start listening and accept encrypted messages.
   * If you type **n**, the script exits so you can edit `keyl_enc.py` manually.

---

### 2) Option B — Build the client separately with build.py

If you want to build the client without running `server.py`, use `build.py`. It asks for confirmation before starting the build.

```bash
# Build a native linux single-file binary
python build.py linux

# Build a Windows executable via wine (if wine is installed)
python build.py windows
```

After a successful build, the executable will be in `./dist/`.

---

### 3) Run the client

* If you did not build, run the client script directly (Python must be present on the machine):

```bash
python keyl_enc.py
```

* If you built the client with PyInstaller, transfer the single-file binary from `dist/` to the target and run it:

```bash
./dist/keyl_enc        # Linux
./dist/keyl_enc.exe    # Windows
```

The client will perform:

1. Fetch server RSA public key.
2. Generate a Fernet key, encrypt with server public RSA key, send it.
3. Send further messages encrypted with Fernet.

---

## Output & logs

* Live in-terminal UI: server prints handshake panel and a live-updating **Incoming Messages** table (via `rich.live.Live`).
* Persistent log: decrypted messages appended to `received_messages.txt` as:

```
[YYYY-MM-DD HH:MM:SS] <message text>
```

---

## Troubleshooting

* **`pyinstaller` not found**: ensure you installed pyinstaller in the same Python environment you're using (e.g., `python -m pip install pyinstaller`).
* **Build fails on wine**: check that wine and a compatible Windows Python are installed and callable as `wine python`. Wine-based builds are environment-sensitive—test on a clean container or VM if possible.
* **Port already in use**: choose another port or `lsof -i :<port>` / `netstat` to find the conflicting process.
* **Remote client can't connect**: ensure firewall/router port-forwarding and that server binds to correct interface (`0.0.0.0` to accept remote connections).

---

## Security & ethics (read this)

This project demonstrates encrypted communication for educational purposes. It can be adapted for legitimate secure telemetry and diagnostics, but **do not use** it to collect data from systems without explicit authorization. Misuse (secret keylogging, unauthorized surveillance, etc.) is unethical and illegal.

By using this code you confirm you will only deploy it on systems you own or have permission to test.

---

## Development notes & tips

* If you plan to extend the system to multiple clients, consider:

  * Using a threaded or async server loop to accept and handle multiple sockets.
  * Per-client session management (storing per-client Fernet keys securely).
* Consider adding message framing (length-prefix) if messages can be larger than the recv buffer.
* For production-level deployment: add authentication, key persistence, certificate-based TLS, and improved error handling.

---


## Example quick commands

```bash
# 1) Install deps
python -m pip install -r requirements.txt

# 2) Edit keyl_enc.py: set HOST and PORT
# 3) Run server (interactive build + start)
python server.py -t 0.0.0.0 -p 4444

# Or build separately for linux
python build.py linux
```


