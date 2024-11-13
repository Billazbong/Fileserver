import socket
import sys
from command_handlers import *

def create_socket():
    """Create a client socket in order to connect to the fileserver 

    Returns:
        socket: the socket which will be used to connect to a fileserver
    """
    try:
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        return client_socket
    except Exception as e:
        print(f"Error creating the socket: {e}")
        sys.exit(1)

def connect_socket(client_socket,host,port):
    """Connect the client socket to a server"""
    try:
        client_socket.connect((host,port))
        print(f"Connected to server {host}:{port}")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)

def handle_command(message):
    """Handle the command entered by the user"""
    parts=message.split()
    if len(parts)==0:
        return
    command=parts[0].lower()
    
    if command not in command_map:
        print(f"Command '{command}' not found")
    else:
        command_map[command](parts)
        

def main():
    if len(sys.argv) != 3:
        print(f"Usage:{sys.argv[0]} <server_host> <server_port>")
        sys.exit(1)
    host=sys.argv[1]
    port=int(sys.argv[2])
    
    client_socket=create_socket()
    connect_socket(client_socket,host,port)
    print("Type 'help' for assistance")
    while(True):
        message=input(f"{os.getcwd()}>")
        handle_command(message)

main()