import os
import socket
import sys
import command_handlers as cmd_h

def create_socket():
    try:
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        return client_socket
    except Exception as e:
        print(f"Error creating the socket: {e}")
        sys.exit(1)

def connect_socket(client_socket,host,port):
    try:
        client_socket.connect((host,port))
        print(f"Connected to server {host}:{port}")
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)

def handle_command(client_socket, message: str):
    parts = message.split()
    if len(parts) == 0:
        return
    command = parts[0].lower()
    
    if command not in cmd_h.command_map:
        print(f"Command '{command}' not found")
    else:
        cmd_h.command_map[command](parts, client_socket)

def discover_servers(broadcast_port:int) -> list:
    """Discover servers on the local network using UDP broadcast."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(3)

    client_socket.sendto("DISCOVER_SERVER".encode(), ('<broadcast>', broadcast_port))
    servers = []
    
    try:
        while True:
            response, addr = client_socket.recvfrom(1024)
            print(f"Received response from {addr}: {response.decode()}")
            servers.append(response.decode())
    except socket.timeout:
        print("Server discovery timed out.")
    return servers

def discover_servers_from_file(broadcast_port,filename):
    """Discover servers on the local network using UDP broadcast and a specific filename"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.settimeout(3)

    client_socket.sendto(f"FILE_DISCOVER_SERVER {filename}".encode(), ('<broadcast>', broadcast_port))
    servers = []
    
    try:
        while True:
            response, addr = client_socket.recvfrom(1024)
            print(f"Received response from {addr}: {response.decode()}")
            servers.append(response.decode())
    except socket.timeout:
        print("Server discovery timed out.")
    return servers


def broadcast():
    broadcast_port = 9999 
    print("Discovering servers on the local network...")
    servers = discover_servers(broadcast_port)
    
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

        print(f"Okay, Connecting...")
        client_socket=create_socket()
        connect_socket(client_socket,host,int(port))
        return client_socket
    else:
        print("No servers found!")
        return 0
    
def find_server_from_file():
    broadcast_port = 9999 
    filename=input("Enter filename>")
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

        print(f"Okay, Connecting...")
        client_socket=create_socket()
        connect_socket(client_socket,host,int(port))
        return client_socket
    else:
        print("No servers found!")
        return 0


def main():
    client_socket=0
    print("Choose how to find servers :")
    print("1. Discover servers")
    print("2. Look for specific file")
    choice=0
    while(client_socket==0 and (choice<1 or choice>2) ):
        try:
            choice=int(input(">"))
            if choice==1:
                client_socket=broadcast()
            elif choice==2:
                client_socket=find_server_from_file()
        except KeyboardInterrupt:
            print("\nGoodbye")
            sys.exit(0)

    print("Type 'help' for assistance")
    while(True):
        try:
            message=input(f"{os.getcwd()}>")
            handle_command(client_socket,message)
        except KeyboardInterrupt:
            print("\nGoodbye")
            sys.exit(0)
main()