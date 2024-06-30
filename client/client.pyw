import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, Listbox, Menu
import socket
import threading
import configparser

# Глобальные переменные
CONFIG_FILE = 'servers.ini'
USER_FILE = 'user.ini'

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой мессенджер")

        # Список серверов
        self.servers = self.load_servers()

        # Имя пользователя
        self.username = self.get_username()

        # Открытие окна выбора сервера
        self.show_server_selection()

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
            username = simpledialog.askstring("Имя пользователя", "Введите ваше имя:")
            if not username:
                messagebox.showerror("Ошибка", "Имя пользователя не может быть пустым!")
                self.root.quit()
            else:
                config['user'] = {'username': username}
                with open(USER_FILE, 'w') as configfile:
                    config.write(configfile)
            return username

    def show_server_selection(self):
        self.clear_window()
        self.root.title("Список серверов")

        self.server_listbox = Listbox(self.root)
        self.server_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        for server in self.servers:
            self.server_listbox.insert(tk.END, server)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=(0, 10))

        add_button = tk.Button(button_frame, text="Добавить сервер", command=self.add_server)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        connect_button = tk.Button(button_frame, text="Подключиться", command=self.connect_to_server)
        connect_button.pack(side=tk.LEFT, padx=(5, 5))
        
        delete_button = tk.Button(button_frame, text="Удалить сервер", command=self.delete_server)
        delete_button.pack(side=tk.LEFT, padx=(5, 0))

    def add_server(self):
        server_name = simpledialog.askstring("Добавить сервер", "Введите имя сервера:")
        server_host = simpledialog.askstring("Добавить сервер", "Введите адрес сервера:")
        server_port = simpledialog.askinteger("Добавить сервер", "Введите порт сервера:")
        
        if server_name and server_host and server_port:
            self.servers[server_name] = f"{server_host}:{server_port}"
            self.save_servers()
            self.server_listbox.insert(tk.END, server_name)

    def delete_server(self):
        selected_server = self.server_listbox.get(tk.ACTIVE)
        if selected_server:
            del self.servers[selected_server]
            self.save_servers()
            self.server_listbox.delete(tk.ACTIVE)

    def connect_to_server(self):
        selected_server = self.server_listbox.get(tk.ACTIVE)
        if selected_server:
            server_info = self.servers[selected_server].split(':')
            self.host = server_info[0]
            self.port = int(server_info[1])
            self.show_chat_window()

    def show_chat_window(self):
        self.clear_window()
        self.root.title(f"Чат - {self.host}:{self.port}")

        # Соединение с сервером и отправка имени пользователя
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(self.username.encode('utf-8'))

        # Создание текстового поля для вывода сообщений
        self.message_display = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.message_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Создание текстового поля для ввода сообщений
        self.message_entry = tk.Entry(self.root, width=60)
        self.message_entry.pack(padx=10, pady=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)

        # Кнопка для отправки сообщения
        send_button = tk.Button(self.root, text="Отправить", command=self.send_message)
        send_button.pack(padx=10, pady=10)

        # Поток для приема сообщений от сервера
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def send_message(self, event=None):
        """
        Отправка сообщения серверу
        """
        message = self.message_entry.get()
        if message:
            self.client_socket.send(f"{self.username}: {message}".encode('utf-8'))
            self.message_display.config(state=tk.NORMAL)
            self.message_display.insert(tk.END, f"You: {message}\n")
            self.message_display.config(state=tk.DISABLED)
            self.message_display.see(tk.END)  # Прокрутка до конца
            self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        """
        Получение сообщений от сервера и вывод на экран
        """
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                self.message_display.config(state=tk.NORMAL)
                self.message_display.insert(tk.END, f"{message}\n")
                self.message_display.config(state=tk.DISABLED)
                self.message_display.see(tk.END)  # Прокрутка до конца
            except Exception as e:
                print(f"[-] Error receiving message: {str(e)}")
                break

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client_app = ClientGUI(root)
    root.mainloop()
