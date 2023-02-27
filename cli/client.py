import socket
import sys
import select

# Define the host and port
HOST = 'localhost'
PORT = 8989

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((HOST, PORT))

# Get the username from the user
while True:
    username_input = input("Enter your username in the format 'username=your_username': ")
    if 'username=' in username_input:
        username = username_input.split('=')[1]
        break
    else:
        print("Invalid username format. Please try again.")

# Send the username to the server
client_socket.send(f"username={username}".encode('utf-8'))

# Wait for the server's welcome message
response = client_socket.recv(1024).decode('utf-8')
print(response)

# Set the socket to non-blocking mode
client_socket.setblocking(False)

while True:
    # Wait for input from the user or data from the server
    ready_to_read, ready_to_write, in_error = select.select([sys.stdin, client_socket], [], [], 0)

    for sock in ready_to_read:
        if sock == client_socket:
            # Receive the response from the server
            response = client_socket.recv(1024).decode('utf-8')

            # If the response is empty, the server has closed the connection
            if not response:
                print("Server closed the connection.")
                client_socket.close()
                sys.exit()

            # Print the response
            print(response)
        else:
            # Get the message from the user
            message = input()

            # Send the message to the server
            client_socket.send(message.encode('utf-8'))

            # If the user wants to exit, close the socket and exit the program
            if message == 'Bye':
                client_socket.close()
                sys.exit()