```markdown
# RAT Demo — Secure Remote CLI

An educational remote administration demonstration project showing how a controlled client-server architecture can be implemented using **TCP sockets, TLS encryption, token authentication, allowlisted Windows commands, logging, and PyInstaller packaging**.

> **Educational Purpose Only:** This project is intended strictly for educational purposes, malware-analysis learning, and authorized cybersecurity testing on systems you own or have explicit permission to use.

## Project Overview

**RAT Demo** demonstrates the architecture and security concepts behind a basic remote administration system in a controlled laboratory environment.

The implementation is intentionally restricted and does **not** provide arbitrary shell execution, persistence, credential theft, evasion, or destructive functionality.

| Component | Details |
|---|---|
| Project | RAT Demo |
| Server | Kali Linux |
| Client | Windows |
| Protocol | TCP + TLS |
| Port | `8443` |
| Authentication | Shared authentication token |
| Commands | Predefined allowlist |
| Logging | Server and client logging |
| Packaging | PyInstaller |
| Windows Deployment | `client.exe` |

## Architecture

```text
                         TLS / TCP :8443

┌─────────────────────┐                     ┌──────────────────────┐
│                     │                     │                      │
│     Kali Linux      │                     │       Windows        │
│                     │                     │                      │
│     server.py       │ ◄────────────────► │   client.py / .exe   │
│                     │       TLS           │                      │
│   Authentication    │                     │  Allowlisted         │
│   Command Handler   │                     │  Commands            │
│   Logging           │                     │                      │
│                     │                     │                      │
└─────────────────────┘                     └──────────────────────┘
```

### Command Flow

```text
Kali Server
     |
     v
Authentication
     |
     v
TLS Connection
     |
     v
Command Request
     |
     v
Allowlist Validation
     |
     v
Windows Command
     |
     v
Command Output
     |
     v
TLS Response
     |
     v
Kali Server
```

## Repository

This project is intended to be published as:

```text
RAT-Demo
```

The original implementation and contributor history should remain properly attributed.

## Project Structure

### Kali Linux

```text
rat-demo/
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
mkdir -p ~/rat-demo/server
mkdir -p ~/rat-demo/logs
cd ~/rat-demo/server
```

## 2. Generate TLS Certificate

Generate a private key:

```bash
openssl genrsa -out server.key 2048
```

Generate a self-signed certificate:

```bash
openssl req -new -x509 -key server.key -out server.crt -days 365 -subj "/CN=RAT-Demo"
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

> **Important:** Never copy `server.key` to the Windows client or publish it to GitHub.

## 3. Generate Authentication Token

Generate a strong random authentication token:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the generated token in both `server.py` and `client.py`:

```python
AUTH_TOKEN = "YOUR_RANDOM_TOKEN"
```

> Never publish the real authentication token in the repository.

## 4. Server Configuration

The server listens on:

```python
HOST = "0.0.0.0"
PORT = 8443
```

Find the Kali Linux IP address:

```bash
ip addr
```

Use the appropriate IP address from your isolated lab network.

## 5. Client Configuration

Configure the Windows client:

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

Replace the example IP with the current Kali Linux IP.

## 6. Start the Kali Server

Navigate to the server directory:

```bash
cd ~/rat-demo/server
```

Start the server:

```bash
python3 server.py
```

Expected output:

```text
============================================================
             RAT DEMO SERVER
============================================================
[*] Server IP : 0.0.0.0
[*] Port      : 8443
[*] Protocol  : TCP + TLS
[*] Commands  : Allowlisted
============================================================

[*] Listening on 0.0.0.0:8443
[*] Waiting for authorized client...
```

Check whether port `8443` is listening:

```bash
sudo ss -lntp | grep 8443
```

## 7. Test Windows Connectivity

From PowerShell:

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

Before packaging the client as an executable:

```powershell
python client.py
```

After successful authentication, the Kali server should display:

```text
[+] TCP/TLS connection from (...)
[+] Client authenticated

rat-demo>
```

## 9. Available Commands

The implementation uses a predefined command allowlist:

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
rat-demo> help
```

Examples:

```text
rat-demo> hostname
rat-demo> whoami
rat-demo> ipconfig
rat-demo> systeminfo
rat-demo> dir
rat-demo> date
```

Exit:

```text
rat-demo> exit
```

The client does **not** accept arbitrary shell commands.

## 10. Build the Windows Executable

Install PyInstaller:

```powershell
pip install pyinstaller
```

Build the executable:

```powershell
pyinstaller --onefile --noconsole --clean client.py
```

The resulting executable will be:

```text
dist\client.exe
```

## 11. Windows Lab Deployment

For the authorized laboratory demonstration, the final Windows machine only needs:

```text
client.exe
```

It does not require:

```text
client.py
server.py
server.key
server.crt
Python
PyInstaller
```

The server-side TLS private key must remain on the server.

## 12. Logging

The Kali server log can be viewed with:

```bash
cat ~/rat-demo/logs/server.log
```

The Windows client generates:

```text
client.log
```

Logging helps demonstrate:

- Client connections
- Authentication events
- Command requests
- Command execution
- Connection errors
- Server activity

## 13. Troubleshooting

### Check Kali IP

```bash
ip addr
```

### Check server port

```bash
sudo ss -lntp | grep 8443
```

### Check Windows IP

```powershell
ipconfig
```

### Test connectivity

```powershell
Test-NetConnection YOUR_KALI_IP -Port 8443
```

### If Kali's IP changes

1. Update `SERVER_HOST` in `client.py`.
2. Rebuild the executable.
3. Copy the new `dist\client.exe` to the authorized Windows laboratory machine.

### Check firewall

```bash
sudo ufw status
```

If required in your isolated lab environment:

```bash
sudo ufw allow 8443/tcp
```

## 14. Security Design

This project demonstrates several cybersecurity and networking concepts:

- TCP socket communication
- TLS-encrypted communication
- Token-based authentication
- JSON message framing
- Command allowlisting
- Command output handling
- Connection logging
- Command logging
- Windows executable packaging
- Kali Linux server deployment
- Basic client-server architecture

The command execution mechanism intentionally validates requested commands against a predefined allowlist instead of accepting arbitrary shell input.

```text
Incoming Command
       |
       v
Command Validation
       |
       +---- Not Allowed ----> Reject
       |
       v
Allowed Command
       |
       v
Windows Execution
       |
       v
Return Output
```

## 15. Security Notes

### TLS Certificate

The educational client uses a self-signed certificate and is configured for a controlled laboratory environment.

This configuration should **not** be considered a production-grade TLS deployment.

For production systems, implement proper certificate validation or mutual TLS (mTLS).

### Authentication Token

Use a strong random token.

Never commit authentication credentials to GitHub.

Do not publish:

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

# TLS private keys
server.key
*.key

# Logs
*.log

# PyInstaller
build/
dist/
*.spec

# Environment files
.env
.env.*

# Local configuration
config.local.*
```

## 17. Source Code

### Server

```text
server.py
```

The server implements:

- TCP communication
- TLS
- Authentication
- Command validation
- Command execution
- Logging
- Client handling

### Client

```text
client.py
```

The client implements:

- TLS connection
- Authentication
- Command requests
- Response handling
- Logging
- Windows command execution

## 18. Educational Scope

```text
                    RAT DEMO
                       |
                       v
              Client / Server Model
                       |
                       v
                 TCP Sockets
                       |
                       v
                 TLS Encryption
                       |
                       v
                Authentication
                       |
                       v
              Command Allowlisting
                       |
                       v
                Command Output
                       |
                       v
                    Logging
                       |
                       v
             Windows EXE Packaging
```

The purpose of this project is to understand the underlying concepts used in remote administration and security tooling while maintaining strict execution controls.

## 19. Limitations

This project is intentionally limited for educational safety and controlled laboratory use.

It does **not** implement:

- Arbitrary remote shell execution
- Persistence mechanisms
- Credential harvesting
- Keylogging
- Security-tool evasion
- Privilege escalation
- Destructive commands
- Unauthorized file collection

The command allowlist is an intentional security control.

## 20. Learning Objectives

After completing this project, you should understand:

1. How TCP client-server communication works.
2. How TLS can protect network traffic.
3. How token-based authentication can be implemented.
4. Why command allowlisting is safer than arbitrary command execution.
5. How command output can be transmitted between systems.
6. How logging supports security monitoring.
7. How Python applications can be packaged using PyInstaller.
8. How a controlled remote administration architecture can be analyzed from a cybersecurity perspective.

## 21. Disclaimer

> **Educational Purpose Only:** RAT Demo is intended solely for educational purposes, malware-analysis learning, cybersecurity research, and authorized laboratory testing.

> Only run this software on systems you own or where you have explicit permission to perform testing.

> The authors are not responsible for misuse, unauthorized access, damage, data loss, or other consequences resulting from the use of this project.

## License

This project is provided under the license included in the repository. Review the license before redistributing or modifying the project.
```
