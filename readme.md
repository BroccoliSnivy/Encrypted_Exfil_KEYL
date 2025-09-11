```markdown
# 🔐 Secure Keylogger

A one-way **encrypted communication system** powered by **RSA** + **Fernet**.  
Built with Python, and comes with a **Rich TUI interface** for pretty outputs, live tables, banners, and build steps.  

---

## ✨ Features
- 🔑 **RSA Key Exchange** – Client receives the server’s RSA public key, and sends back a Fernet session key.
- 🛡 **Fernet Encryption** – All messages are AES-256 encrypted (via Fernet).
- 🖥 **Rich TUI** – Beautiful banners, live message table, build panels, and colored logs.
- 📝 **Message Logging** – All received messages are saved to `received_messages.txt`.
- ⚙️ **Flexible Builds** –  
  - `server.py` can build the client automatically (PyInstaller).  
  - Or use `build.py` separately for **Linux** or **Windows (via Wine)** builds.

---

## 📂 Project Structure
```

.
├── server.py        # Main server (runs encryption, logging, build option)
├── keyl\_enc.py      # Client (sender) – must edit HOST + PORT before build
├── build.py         # Standalone build helper (Linux or Windows via Wine)
├── received\_messages.txt   # Generated log file for received messages
└── dist/            # Auto-generated executables (after build)

````

---

## 🛠 Requirements
Make sure you have:
- Python **3.8+**
- `pip install cryptography rich pyinstaller`
- (Optional) **Wine** if you want to build Windows `.exe` from Linux

---

## 🚀 Usage

### 1️⃣ Setup Server
```bash
python server.py -t <server-ip> -p <port>
````

* Shows a **banner + instructions**.
* Asks if you want to **build client** (`keyl_enc.py`) before starting server.

Example:

```bash
python server.py -t 127.0.0.1 -p 5000
```

---

### 2️⃣ Configure Client

Open `keyl_enc.py` and set:

```python
HOST = "127.0.0.1"   # your server IP
PORT = 5000          # same port as server
```

---

### 3️⃣ Build Client

#### Option A – Let `server.py` handle it

It will ask you and build automatically.

#### Option B – Use standalone `build.py`

Build for Linux:

```bash
python build.py linux
```

Build for Windows (via Wine):

```bash
python build.py windows
```

✅ Output binary will appear inside `dist/`

---

### 4️⃣ Run Client

Just execute the built binary:

```bash
./dist/keyl_enc       # Linux
./dist/keyl_enc.exe   # Windows
```

---

## 📖 How It Works

1. Server generates **RSA key pair** and sends public key → Client.
2. Client generates a **Fernet session key**, encrypts with RSA, sends back → Server.
3. All further communication is **Fernet-encrypted**.
4. Server:

   * Decrypts client messages.
   * Shows them in a **live Rich table**.
   * Logs into `received_messages.txt`.

---

## ⚡ Example Flow

1. Start server:

   ```
   python server.py -t 192.168.1.10 -p 5000
   ```
2. It asks:

   ```
   Before continuing, edit keyl_enc.py and set HOST and PORT.
   Wanna proceed? (y/n)
   ```
3. You say **y**, it builds the client, then listens.
4. Client runs and sends messages securely.
5. Server shows them live and logs to file.

---

## 🎯 Roadmap (Future Ideas)

* 🔄 Full duplex chat (two-way).
* 📦 File sharing with encryption.
* 🌐 Multiple clients support.
* 🐳 Docker container setup for quick deployment.

---
