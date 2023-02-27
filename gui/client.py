import tkinter as tk
import socket
import threading

# Define the host and port
HOST = 'localhost'
PORT = 8989

# Create the client socket and connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Ask the user for their username
username = input("Enter your username: ")
if not username:
    print("Please enter a username.")
    sys.exit()

# Send the username to the server
client_socket.send(f"username = {username}".encode('utf-8'))

# Function to send messages to the server
def send_message(event=None):
    message = message_entry.get()
    client_socket.send(message.encode('utf-8'))
    message_entry.delete(0, tk.END)

# Function to handle incoming messages
def handle_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break
        message_listbox.insert(tk.END, message)

# Create the GUI window
root = tk.Tk()
root.title("Chat App")

# Create the message display area
message_frame = tk.Frame(root)
message_scrollbar = tk.Scrollbar(message_frame)
message_listbox = tk.Listbox(message_frame, height=20, width=50, yscrollcommand=message_scrollbar.set)
message_scrollbar.config(command=message_listbox.yview)
message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
message_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
message_frame.pack()

# Create the message input area
input_frame = tk.Frame(root)
message_entry = tk.Entry(input_frame, width=50)
message_entry.bind("<Return>", send_message)
send_button = tk.Button(input_frame, text="Send", command=send_message)
message_entry.pack(side=tk.LEFT, padx=5, pady=5, expand=True, fill=tk.X)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)
input_frame.pack()

# Start the message handling thread
threading.Thread(target=handle_messages).start()

# Start the GUI event loop
root.mainloop()