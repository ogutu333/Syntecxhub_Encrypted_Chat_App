import socket
import threading
import json
import logging

HOST = "0.0.0.0"
PORT = 5000

clients = {}
clients_lock = threading.Lock()

logging.basicConfig(
    filename="logs/chat.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def send_json(sock, data):
    message = json.dumps(data) + "\n"
    sock.sendall(message.encode())

def broadcast(data, exclude=None):
    message = (json.dumps(data) + "\n").encode()

    with clients_lock:
        recipients = list(clients.items())

    for sock, nickname in recipients:
        if sock == exclude:
            continue
        try:
            sock.sendall(message)
        except OSError:
            remove_client(sock)

def remove_client(sock):
    with clients_lock:
        nickname = clients.pop(sock, None)

    if nickname:
        logging.info("Disconnected: %s", nickname)
        try:
            sock.close()
        except OSError:
            pass
        broadcast({
            "type": "system",
            "message": f"{nickname} left the chat."
        })


def handle_client(sock, address):
    nickname = None
    try:
        reader = sock.makefile("r")
        # First message establishes the nickname
        join_data = json.loads(reader.readline())

        if join_data.get("type") != "join":
            return

        nickname = join_data.get("nickname", "Anonymous")

        with clients_lock:
            clients[sock] = nickname

        logging.info("Connected: %s from %s", nickname, address)

        broadcast({
            "type": "system",
            "message": f"{nickname} joined the chat."
        })

        while True:
            line = reader.readline()

            if not line:
                break

            data = json.loads(line)

            if data.get("type") == "message":
                payload = data.get("payload", "")
                logging.info(
                    "Encrypted message from %s: %s",
                    nickname,
                    payload
                )
                broadcast({
                    "type": "message",
                    "sender": nickname,
                    "payload": payload
                })
            elif data.get("type") == "quit":
                break
    except (OSError, json.JSONDecodeError) as error:
        logging.warning(
            "Client error from %s: %s",
            address,
            error
        )
    finally:
        if nickname:
            remove_client(sock)

def start_server():
    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server.bind((HOST, PORT))
    server.listen()
    print(f"Chat server running on {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, address),
            daemon=True
        )
        thread.start()

if __name__ == "__main__":
    start_server()