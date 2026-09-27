import socket
import ssl
import json
import secrets
import datetime
import os

HOST = "0.0.0.0"
PORT = 8443
CERT_FILE = "server.crt"
KEY_FILE = "server.key"
AUTH_TOKEN = "fSwscUi04xXkA9bP7PxT5jThHPwqzCyhWpIgPBSN17Q"

LOG_DIR = "../logs"
LOG_FILE = os.path.join(LOG_DIR, "server.log")


def log(message):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")


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
            raise ConnectionError("Connection closed")
        data += part

    return json.loads(data.decode())


def authenticate(sock):
    send_json(sock, {"type": "auth_request"})
    response = receive_json(sock)

    if not response or response.get("type") != "auth":
        return False

    token = response.get("token", "")

    if secrets.compare_digest(token, AUTH_TOKEN):
        send_json(sock, {
            "type": "auth_response",
            "status": "success"
        })
        return True

    send_json(sock, {
        "type": "auth_response",
        "status": "failed"
    })
    return False


def handle_client(sock, address):
    print(f"\n[+] TLS client: {address}")
    log(f"CONNECT {address}")

    try:
        if not authenticate(sock):
            print("[!] Authentication failed.")
            log(f"AUTH FAILED {address}")
            return

        print("[+] Authenticated.")

        while True:
            command = input("\nsecure-cli> ").strip()

            if not command:
                continue

            send_json(sock, {
                "type": "command",
                "command": command
            })

            log(f"SEND {address}: {command}")

            if command.lower() == "exit":
                break

            response = receive_json(sock)

            if not response:
                print("[!] Client disconnected.")
                break

            output = response.get("output", "")
            cwd = response.get("cwd", "")

            print(output, end="" if output.endswith("\n") else "\n")

            if cwd:
                print(f"[client cwd: {cwd}]")

            log(f"RECV {address}: {output[:4000]}")

    except (ConnectionError, ConnectionResetError, BrokenPipeError, OSError) as e:
        print(f"\n[!] Client disconnected: {e}")
        log(f"DISCONNECT {address}: {e}")

    except KeyboardInterrupt:
        raise

    except Exception as e:
        print(f"\n[!] Session error: {e}")
        log(f"ERROR {address}: {e}")

    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            sock.close()
        except Exception:
            pass

        print("[*] Connection closed.")
        log(f"CLOSE {address}")


def main():
    os.makedirs(LOG_DIR, exist_ok=True)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[*] TLS lab server listening on {HOST}:{PORT}")
    log(f"SERVER START {HOST}:{PORT}")

    try:
        while True:
            raw, address = server.accept()

            try:
                tls = ctx.wrap_socket(
                    raw,
                    server_side=True
                )
                handle_client(tls, address)

            except ssl.SSLError as e:
                print(f"[!] TLS error: {e}")
                log(f"TLS ERROR: {e}")
                raw.close()

    except KeyboardInterrupt:
        print("\n[*] Server stopped.")

    finally:
        server.close()
        log("SERVER STOP")


if __name__ == "__main__":
    main()