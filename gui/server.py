import threading
import socket
import tkinter as tk


class ServerGUI:
    def __init__(self, master):
        self.master = master
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8989))
        self.server_socket.listen()
        self.server_thread = None
        self.output_text = None
        self.start_button = None
        self.stop_button = None
        self.quit_button = None

        # GUI setup
        self.output_text = tk.Text(master)
        self.output_text.pack()

        self.start_button = tk.Button(master, text="Start Server", command=self.start_server)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop Server", command=self.stop_server, state="disabled")
        self.stop_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def start_server(self):
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.output_text.insert(tk.END, "Server started.\n")

    def stop_server(self):
        self.stop_button.config(state="disabled")

        self.output_text.insert(tk.END, "Stopping server...\n")

        for client in self.clients:
            client.close()

        self.server_socket.close()

        self.output_text.insert(tk.END, "Server stopped.\n")
        self.start_button.config(state="normal")

    def run_server(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        username = None

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')

                if not message:
                    self.clients.remove(client_socket)
                    print(f"Client {client_address} disconnected.")
                    break

                if 'username =' in message:
                    username = message.split('=')[1].strip()
                    print(f"Server: Welcome {username}")
                    self.broadcast(f"Server: Welcome {username}")
                elif message == 'AllUsers':
                    active_users = [c.getpeername()[0] for c in self.clients]
                    client_socket.send(f"All active users: {', '.join(active_users)}".encode('utf-8'))
                elif message == 'Bye':
                    print(f"Server: Goodbye {username}")
                    self.broadcast(f"Server: Goodbye {username}")
                    self.clients.remove(client_socket)
                    break
                else:
                    print(f"{username}: {message}")
                    self.broadcast(f"{username}: {message}")
            except ConnectionResetError:
                self.clients.remove(client_socket)
                print(f"Client {client_address} disconnected.")
                break

        client_socket.close()

    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(message.encode('utf-8'))
            except ConnectionResetError:
                self.clients.remove(client)
                print(f"Client {client.getpeername()[0]} disconnected.")


if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()