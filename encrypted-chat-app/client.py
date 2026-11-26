import socket
import threading
import json

from crypto_utils import load_key, encrypt_message, decrypt_message

HOST = "127.0.0.1"
PORT = 5000

def send_json(sock, data):
    message = json.dumps(data) + "\n"
    sock.sendall(message.encode())

def receive_messages(sock, key):
    reader = sock.makefile("r")
    try:
        while True:
            line = reader.readline()
            if not line:
                print("\nDisconnected from server.")
                break

            data = json.loads(line)
            if data["type"] == "system":
                print(f"\n[System] {data['message']}")
            elif data["type"] == "message":
                try:
                    plaintext = decrypt_message(
                        data["payload"],
                        key
                    )
                    print(
                        f"\n{data['sender']}: {plaintext}"
                    )
                except Exception:
                    print(
                        f"\n[Security] Invalid or "
                        f"tampered message from {data['sender']}"
                    )
    except (OSError, json.JSONDecodeError):
        print("\nError receiving messages.")
    finally:
        sock.close()

def start_client():
    nickname = input("Enter your nickname: ")
    key = load_key()
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    client_socket.connect((HOST, PORT))
    send_json(client_socket, {
        "type": "join",
        "nickname": nickname
    })
    receiver = threading.Thread(
        target=receive_messages,
        args=(client_socket, key),
        daemon=True
    )
    receiver.start()
    print("Connected. Type /quit to exit.")
    try:
        while True:
            message = input()
            if message == "/quit":
                send_json(client_socket, {
                    "type": "quit"
                })
                break
            encrypted_message = encrypt_message(
                message,
                key
            )
            send_json(client_socket, {
                "type": "message",
                "payload": encrypted_message
            })
    except (KeyboardInterrupt, EOFError):
        print("\nExiting chat.")
    finally:
        try:
            client_socket.close()
        except OSError:
            pass

if __name__ == "__main__":
    start_client()