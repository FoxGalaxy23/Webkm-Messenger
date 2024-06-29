import socket
import threading

# Глобальные переменные
HOST = '26.197.218.121'  # Локальный адрес сервера
PORT = 12345  # Порт для соединения
clients = []  # Список подключенных клиентов

def handle_client(client_socket, addr):
    """
    Обработчик подключенного клиента
    """
    print(f"[+] New connection from {addr}")

    try:
        # Принимаем имя пользователя
        username = client_socket.recv(1024).decode('utf-8')
        print(f"[*] Username set for {addr}: {username}")

        broadcast(f"{username} присоединился к чату", client_socket)

        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"Received from {username}: {message}")
            broadcast(f"{username}: {message}", client_socket)
    except Exception as e:
        print(f"[-] Error handling client {addr}: {str(e)}")
    finally:
        broadcast(f"{username} покинул чат", client_socket)
        client_socket.close()
        clients.remove(client_socket)
        print(f"[-] Connection closed with {addr}")

def broadcast(message, sender_socket):
    """
    Рассылка сообщения всем клиентам, кроме отправителя
    """
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"[-] Error broadcasting to a client: {str(e)}")

def start_server():
    """
    Запуск сервера
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[*] Listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)

            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
