# Secure Remote CLI

A small educational remote CLI project demonstrating **TCP sockets, TLS encryption, token authentication, allowlisted Windows commands, logging, and PyInstaller packaging**.

> **Educational Purpose Only:** This project is created strictly for educational purposes and authorized cybersecurity testing on systems you own or have explicit permission to use.

## Project Overview

| Component | Details |
|---|---|
| Server | Kali Linux |
| Client | Windows |
| Protocol | TCP + TLS |
| Port | `8443` |
| Authentication | Shared token |
| Commands | Allowlisted only |
| Windows deployment | `client.exe` |

The Windows client is intentionally restricted to predefined commands and does not provide an arbitrary command shell, persistence, credential theft, or security-tool evasion. fileciteturn0file0L1-L9

## Architecture

```text
                    TLS / TCP :8443
┌──────────────┐                         ┌──────────────────┐
│ Kali Linux   │                         │ Windows          │
│ server.py    │ ──────────────────────> │ client.exe       │
│ secure-cli>  │ <────────────────────── │ allowlisted      │
└──────────────┘        output            │ commands         │
                                         └──────────────────┘
```

## Repository

- **Repository:** https://github.com/arthghori/Remote-CLI
- **Server:** https://github.com/arthghori/Remote-CLI/blob/main/server.py
- **Client:** https://github.com/arthghori/Remote-CLI/blob/main/client.py

## Project Structure

### Kali Linux

```text
secure-remote-cli/
├── server/
│   ├── server.py
│   ├── server.crt
│   └── server.key
└── logs/
    └── server.log
```

### Windows Development

```text
client/
└── client.py
```

### Windows After Packaging

```text
client/
└── dist/
    └── client.exe
```

## 1. Kali Linux Setup

```bash
mkdir -p ~/secure-remote-cli/server
mkdir -p ~/secure-remote-cli/logs
cd ~/secure-remote-cli/server
```

## 2. Generate TLS Certificate

```bash
openssl genrsa -out server.key 2048
```

```bash
openssl req -new -x509 -key server.key -out server.crt -days 365 -subj "/CN=SecureRemoteCLI"
```

Verify:

```bash
ls -l
```

You should have:

```text
server.crt
server.key
```

**Important:** Never copy `server.key` to the Windows client.

## 3. Generate Authentication Token

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the same generated token in both `server.py` and `client.py`.

```python
AUTH_TOKEN = "YOUR_RANDOM_TOKEN"
```

Do not publish the real token in GitHub.

## 4. Server Configuration

Keep the server listening configuration as:

```python
HOST = "0.0.0.0"
PORT = 8443
```

Find the Kali IP with:

```bash
ip addr
```

## 5. Client Configuration

Set the current Kali IP in `client.py`:

```python
SERVER_HOST = "YOUR_KALI_IP"
SERVER_PORT = 8443
AUTH_TOKEN = "YOUR_RANDOM_TOKEN"
```

Example:

```python
SERVER_HOST = "192.168.31.251"
SERVER_PORT = 8443
```

Replace the example with your current Kali IP.

## 6. Start the Kali Server

```bash
cd ~/secure-remote-cli/server
python3 server.py
```

Expected:

```text
============================================================
       SECURE REMOTE CLI SERVER
============================================================
[*] Server IP : 0.0.0.0
[*] Port      : 8443
[*] Protocol  : TCP + TLS
[*] Commands  : Allowlisted
============================================================

[*] Listening on 0.0.0.0:8443
[*] Waiting for authorized client...
```

Check port `8443`:

```bash
sudo ss -lntp | grep 8443
```

## 7. Test Windows Connectivity

PowerShell:

```powershell
ping YOUR_KALI_IP
```

Then:

```powershell
Test-NetConnection YOUR_KALI_IP -Port 8443
```

Expected:

```text
TcpTestSucceeded : True
```

## 8. Test the Python Client

Before creating the EXE:

```powershell
python client.py
```

After successful authentication, Kali should show:

```text
[+] TCP/TLS connection from (...)
[+] Client authenticated

secure-cli>
```

## 9. Available Commands

The implementation uses an allowlist:

```text
whoami
hostname
ipconfig
systeminfo
dir
date
```

Use:

```text
secure-cli> help
```

Examples:

```text
secure-cli> hostname
secure-cli> whoami
secure-cli> ipconfig
secure-cli> systeminfo
secure-cli> dir
secure-cli> date
```

Exit:

```text
secure-cli> exit
```

The command flow is:

```text
Kali secure-cli
      |
      v
server.py
      |
      | TLS
      v
client.py / client.exe
      |
      v
Allowlisted Windows command
      |
      v
Command output
      |
      | TLS
      v
Kali server
```

## 10. Build the Windows EXE

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build:

```powershell
pyinstaller --onefile --noconsole --clean client.py
```

Final executable:

```text
dist\client.exe
```

## 11. Windows Final Lab Machine

For the authorized lab demonstration, the final Windows machine only needs:

```text
client.exe
```

It does not need:

```text
client.py
server.py
server.key
server.crt
Python
PyInstaller
```

## 12. Logging

Kali server log:

```bash
cat ~/secure-remote-cli/logs/server.log
```

Windows client log:

```text
client.log
```

## 13. Troubleshooting

Check Kali IP:

```bash
ip addr
```

Check server port:

```bash
sudo ss -lntp | grep 8443
```

Check Windows IP:

```powershell
ipconfig
```

Test connectivity:

```powershell
Test-NetConnection YOUR_KALI_IP -Port 8443
```

If Kali's IP changes:

1. Update `SERVER_HOST` in `client.py`.
2. Rebuild the EXE.
3. Copy the new `dist\client.exe` to the authorized Windows test machine.

If UFW is enabled in your isolated lab:

```bash
sudo ufw status
```

If required:

```bash
sudo ufw allow 8443/tcp
```

## 14. Security Design

This project demonstrates:

- TCP socket communication
- TLS-encrypted communication
- Token-based authentication
- JSON message framing
- Command allowlisting
- Command output handling
- Connection and command logging
- Windows executable packaging
- Kali Linux server deployment

The implementation intentionally checks requested commands against a predefined allowlist instead of accepting arbitrary shell input. fileciteturn0file0L1356-L1369

## 15. Security Notes

### TLS Certificate

The educational client uses a self-signed certificate and disables normal certificate verification. This is suitable only for an isolated lab demonstration.

For production use, implement proper certificate validation or mutual TLS (mTLS).

### Authentication Token

Use a strong random token and never publish it in the GitHub repository.

Do not commit:

```text
server.key
AUTH_TOKEN
client.log
server.log
```

## 16. Recommended `.gitignore`

```gitignore
__pycache__/
*.pyc
server.key
*.log
build/
dist/
*.spec
.env
```

## 17. Source Code

### Server

Complete `server.py`:

https://github.com/arthghori/Remote-CLI/blob/main/server.py

### Client

Complete `client.py`:

https://github.com/arthghori/Remote-CLI/blob/main/client.py

## 18. Educational Scope

```text
Networking
   ↓
TCP sockets
   ↓
TLS encryption
   ↓
Authentication
   ↓
Allowlisted commands
   ↓
Output handling
   ↓
Logging
   ↓
Executable packaging
```

> **Educational Purpose Only:** Use this project only on systems you own or where you have explicit authorization to perform testing. Do not use it for unauthorized access, persistence, credential theft, evasion, or other harmful activity.

## License

Add the license that matches your project requirements before publishing or distributing the repository.

