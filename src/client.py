import os
import socket
import sys
import command_handlers as cmd_h

RESET = "\033[0m"
LIGHT_PURPLE = "\033[95m"
LIGHT_GREEN = "\033[92m"
LIGHT_BLUE = "\033[94m"
LIGHT_YELLOW = "\033[93m"
LIGHT_RED = "\033[91m"

def create_socket():
    """
    Create a new TCP socket.

    Returns:
        socket.socket: A newly created socket.
    """
    try:
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        return client_socket
    except Exception as e:
        print(f"Error creating the socket: {e}")
        sys.exit(1)

def connect_socket(client_socket,host,port):
    """
    Connect the given socket to a server at the specified host and port.

    Args:
        client_socket (socket.socket): The client socket to connect.
        host (str): The server host or IP address.
        port (int): The server port number.

    Returns:
        None
    """
    try:
        client_socket.connect((host,port))
        print(LIGHT_YELLOW + f"[+] Connected to server {host}:{port}" + RESET)
    except Exception as e:
        print(LIGHT_RED + f"Error connecting to server: {e}" + RESET)
        sys.exit(1)

def handle_command(client_socket:int, message: str):
    """
    Parse and handle a command entered by the user.

    Args:
        client_socket (socket.socket): The connected client socket.
        message (str): The command line input from the user.

    Returns:
        None
    """
    parts = message.split()
    if len(parts) == 0:
        return
    command = parts[0].lower()
    
    if command not in cmd_h.command_map:
        print(LIGHT_RED + f"Command '{command}' not found" + RESET)
    else:
        cmd_h.command_map[command](parts, client_socket)

def discover_servers(broadcast_port:int) -> list:
    """
    Discover servers on the local network using UDP broadcast.

    Args:
        broadcast_port (int): The UDP broadcast port number.

    Returns:
        list: A list of server responses in the form 'ip:port'.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(3)

    client_socket.sendto("DISCOVER_SERVER".encode(), ('<broadcast>', broadcast_port))
    servers = []
    
    try:
        while True:
            response, addr = client_socket.recvfrom(1024)
            print(LIGHT_YELLOW + f"[+] Received response from {addr} : {response.decode()}" + RESET)
            servers.append(response.decode())
    except socket.timeout:
        if len(servers) == 0 :
            print(LIGHT_RED + "Server discovery timed out." + RESET)
    return servers

def discover_servers_from_file(broadcast_port:int,filename:str):
    """
    Discover servers on the local network that have a specific file, using UDP broadcast.

    Args:
        broadcast_port (int): The UDP broadcast port.
        filename (str): The name of the file to discover.

    Returns:
        list: A list of server responses in the form 'ip:port' for servers that have the file.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(3)

    client_socket.sendto(f"FILE_DISCOVER_SERVER {filename}".encode(), ('<broadcast>', broadcast_port))
    servers = []
    
    try:
        while True:
            response, addr = client_socket.recvfrom(1024)
            print(LIGHT_YELLOW + f"Received response from {addr}: {response.decode()} + RESET")
            servers.append(response.decode())
    except socket.timeout:
        if len(servers) == 0 :
            print(LIGHT_RED + "Server discovery timed out." + RESET)
    return servers

def broadcast():
    """
    Discover servers on the local network and allow the user to choose one to connect to.

    Returns:
        socket.socket or int: A connected client socket if successful, 0 if no servers are found.
    """
    broadcast_port = 9999 
    print(LIGHT_YELLOW + "Discovering servers on the local network..." + RESET)
    servers = discover_servers(broadcast_port)
    
    if servers:
        if len(servers) == 1:
            # If only one server found, connect directly
            print(LIGHT_YELLOW + f"    Connecting to {servers[0]}...")
            host, port = servers[0].split(":") 
        else:
            print(LIGHT_GREEN + f"[+] Found servers: \n" + RESET + "\n".join((LIGHT_BLUE + f"{i} > {servers[i]}" + RESET for i in range(1, len(servers)))))
            # If multiple servers found, let the user choose
            c = -1
            while (c not in range (1, len(servers)+1)):
                print(f"Which server do you want to connect to ? ( 1 - {len(servers)} )\n")
                c = int(input("> "))
            host, port = servers[c-1].split(":") 

        client_socket = create_socket()
        connect_socket(client_socket,host,int(port))
        return client_socket
    else:
        print("[-] No servers found!")
        return 0

def find_server_from_file():
    """
    Discover servers on the local network that contain a specific file and allow the user to choose one to connect to.

    Returns:
        socket.socket or int: A connected client socket if successful, 0 if no servers are found.
    """
    broadcast_port = 9999 
    filename=input("Enter filename \n> ")
    print("Discovering servers on the local network...")
    servers = discover_servers_from_file(broadcast_port,filename)
    
    if servers:
        print(f"[+] Found servers: \n" + "\n".join((f"{i} > {servers[i]}" for i in range(1, len(servers)))))
        if len(servers) == 1:
            print(f"Connecting to {servers[0]}...")
            host, port = servers[0].split(":") 
        else:
            c = -1
            while (c not in range (1, len(servers)+1)):
                print(f"Which server do you want to connect to ? ( 1 - {len(servers)} )")
                c = int(input("> "))
            host, port = servers[c-1].split(":") 

        client_socket=create_socket()
        connect_socket(client_socket,host,int(port))
        return client_socket
    else:
        print("No servers found!")
        return 0

def main():
    """
    The main function handling:
    - Discovering servers or files on the network.
    - Connecting to the chosen server.
    - Interactively handling user commands until interrupted.
    """
    client_socket = 0
    choice = 0
    while(client_socket == 0 or choice < 1 or choice > 2):
        try:
            print("+===========================+")
            print("|       " + LIGHT_PURPLE + "File Server" + RESET + "         |")
            print("+---------------------------+")
            print("| Choose how to find servers|")
            print("| "+ LIGHT_GREEN + "1. Discover servers" + RESET + "       |")
            print("| "+ LIGHT_GREEN + "2. Look for specific file" + RESET + " |")
            print("+===========================+")

            choice = int(input("> "))
            if choice == 1:
                client_socket = broadcast()
            elif choice == 2:
                client_socket = find_server_from_file()
        except KeyboardInterrupt:
            print("\n" + LIGHT_PURPLE +"Goodbye o/" + RESET)
            sys.exit(0)

    print(LIGHT_GREEN + "Type 'help' for assistance" + RESET)
    while True:
        try:
            message = input(LIGHT_BLUE + f"{ os.getcwd() } > " + RESET)
            handle_command(client_socket,message)
        except KeyboardInterrupt:
            print("\n" + LIGHT_PURPLE +"Goodbye o/"+ RESET)
            sys.exit(0)

if __name__ == "__main__":
    main()
