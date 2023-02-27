import threading
import socket

# Define the host and port
HOST = 'localhost'
PORT = 8989

# Store the list of connected clients
clients = []

# Maximum capacity for the number of clients
MAX_CLIENTS = 10

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

# Function to handle messages from clients
def handle_client(client_socket, client_address):
    username = None
    while True:
        try:
            # Receive the message from the client
            message = client_socket.recv(1024).decode('utf-8')

            # If the client has disconnected, remove them from the list
            if not message:
                clients.remove(client_socket)
                print(f"Client {client_address} disconnected.")
                break

            # If the client is sending their username
            if message.startswith('username='):
                username = message.split('=')[1].strip()
                client_socket.send(f"Server: Welcome {username}\n".encode('utf-8'))
                broadcast(f"Server: {username} has joined the chat.")
            # If the client wants to see all active users
            elif message == 'AllUsers':
                active_users = [c.getpeername()[0] for c in clients]
                client_socket.send(f"All active users: {', '.join(active_users)}".encode('utf-8'))
            # If the client wants to leave
            elif message == 'Bye':
                print(f"Server: Goodbye {username}")
                broadcast(f"Server: {username} has left the chat.")
                clients.remove(client_socket)
                break
            # If it's a regular message, broadcast it to all clients
            else:
                if username:
                    print(f"{username}: {message}")
                    broadcast(f"{username}: {message}")
                else:
                    client_socket.send("Server: Please send your username as 'username=your_username'\n".encode('utf-8'))
        except ConnectionResetError:
            clients.remove(client_socket)
            print(f"Client {client_address} disconnected.")
            break

    client_socket.close()


# Function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

# Continuously listen for incoming connections
try:
    while True:
        # Check if the maximum capacity has been reached
        if len(clients) >= MAX_CLIENTS:
            print(f"Maximum capacity ({MAX_CLIENTS}) reached. Waiting for clients to disconnect...")
            while len(clients) >= MAX_CLIENTS:
                pass
            print(f"Maximum capacity reduced. Resuming accepting clients...")

        print('Server waiting for connection...')
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        print(f"Client {client_address} connected.")
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

# Gracefully handle Ctrl+C
except KeyboardInterrupt:
    print("\nClosing server...")
    for client_socket in clients:
        client_socket.close()
    server_socket.close()
    print("Server closed.")