import os
import socket
import sys
import command_handlers as cmd_h

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
    
    if command not in cmd_h.command_map:
        print(f"Command '{command}' not found")
    else:
        cmd_h.command_map[command](parts)

def discover_servers(broadcast_port):
    """Discover servers on the local network using UDP broadcast."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(5)  # Wait for 5 seconds for responses

    message = "DISCOVER_SERVER"
    client_socket.sendto(message.encode(), ('<broadcast>', broadcast_port))
    servers = []
    
    try:
        while True:
            response, addr = client_socket.recvfrom(1024)
            print(f"Received response from {addr}: {response.decode()}")
            servers.append(response.decode())
    except socket.timeout:
        print("Server discovery timed out.")

    return servers        


def main():
    
    broadcast_port = 9999  # Port to send and listen for discovery messages
    print("Discovering servers on the local network...")
    servers = discover_servers(broadcast_port)
    
    if servers:
        print(f"Found servers: {servers}")
        # You can now connect to one of the servers (e.g., based on response or user choice)
        chosen_server = servers[0]  # Just pick the first one for simplicity
        print(f"Connecting to {chosen_server}")
        host, port = chosen_server.split(":")
        connect_socket(host, int(port))
    else:
        print("No servers found!")
    
    if len(sys.argv) != 3:
        print(f"Usage:{sys.argv[0]} <server_host> <server_port>")
        sys.exit(1)
    host=sys.argv[1]
    port=int(sys.argv[2])
    
    client_socket=create_socket()
    connect_socket(client_socket,host,port)
    print("Type 'help' for assistance")
    while(True):
        try:
            message=input(f"{os.getcwd()}>")
            handle_command(message)
        except KeyboardInterrupt:
            print("\nGoodbye")
            sys.exit(0)

main()