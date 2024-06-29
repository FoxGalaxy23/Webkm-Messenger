import socket
import threading
import configparser

# Глобальные переменные
CONFIG_FILE = 'servers.ini'
USER_FILE = 'user.ini'


class ClientCLI:
    def __init__(self):
        self.servers = self.load_servers()
        self.username = self.get_username()
        self.main_menu()

    def load_servers(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        if 'servers' not in config:
            config['servers'] = {}
        return config['servers']

    def save_servers(self):
        config = configparser.ConfigParser()
        config['servers'] = self.servers
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    def get_username(self):
        config = configparser.ConfigParser()
        config.read(USER_FILE)
        if 'user' in config and 'username' in config['user']:
            return config['user']['username']
        else:
            username = input("Введите ваше имя: ").strip()
            if not username:
                print("Имя пользователя не может быть пустым!")
                exit(1)
            else:
                config['user'] = {'username': username}
                with open(USER_FILE, 'w') as configfile:
                    config.write(configfile)
            return username

    def main_menu(self):
        while True:
            print("\n1. Список серверов")
            print("2. Добавить сервер")
            print("3. Удалить сервер")
            print("4. Подключиться к серверу")
            print("5. Выйти")
            choice = input("Выберите действие: ").strip()
            if choice == '1':
                self.list_servers()
            elif choice == '2':
                self.add_server()
            elif choice == '3':
                self.delete_server()
            elif choice == '4':
                self.connect_to_server()
            elif choice == '5':
                break
            else:
                print("Неверный выбор, попробуйте снова.")

    def list_servers(self):
        if not self.servers:
            print("Список серверов пуст.")
        else:
            print("\nСписок серверов:")
            for name, addr in self.servers.items():
                print(f"{name}: {addr}")

    def add_server(self):
        server_name = input("Введите имя сервера: ").strip()
        server_host = input("Введите адрес сервера: ").strip()
        server_port = input("Введите порт сервера: ").strip()

        if server_name and server_host and server_port:
            self.servers[server_name] = f"{server_host}:{server_port}"
            self.save_servers()
            print("Сервер добавлен.")

    def delete_server(self):
        server_name = input("Введите имя сервера для удаления: ").strip()
        if server_name in self.servers:
            del self.servers[server_name]
            self.save_servers()
            print("Сервер удален.")
        else:
            print("Сервер не найден.")

    def connect_to_server(self):
        server_name = input("Введите имя сервера для подключения: ").strip()
        if server_name in self.servers:
            server_info = self.servers[server_name].split(':')
            self.host = server_info[0]
            self.port = int(server_info[1])
            self.start_chat()
        else:
            print("Сервер не найден.")

    def start_chat(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.username.encode('utf-8'))

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        print(f"Подключено к серверу {self.host}:{self.port}")
        print("Введите ваше сообщение и нажмите Enter. Для выхода введите 'exit'.")

        while True:
            message = input()
            if message.lower() == 'exit':
                self.client_socket.close()
                break
            if message:
                self.client_socket.send(f"{self.username}: {message}".encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                print(f"\n{message}")
            except Exception as e:
                print(f"Ошибка при получении сообщения: {str(e)}")
                break


if __name__ == "__main__":
    client_app = ClientCLI()
