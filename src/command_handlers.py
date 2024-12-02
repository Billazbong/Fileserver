import os
import socket

# Dictionary to store commands (mostly used for 'help')
commands = {
    'help' : 'Displays the list of all commmands or provides more detail on a specific command.\nUsage : help [<command>]',
    'list' : 'Lists all the files in the current directory of the fileserver.\nUsage : list',
    'llist' : 'Lists all the files in the current directory of the client.\nUsage : llist',
    'pwd' : 'Returns the name of the current directory of the fileserver.\nUsage : pwd',
    'lpwd' : 'Returns the name of the current directory of the client.\nUsage : lpwd',
    'cd' : 'Accesses the given directory in the current directory of the fileserver.\nUsage : cd <directory>',
    'lcd' : 'Accesses the given directory in the current directory of the client.\nUsage : lcd <directory>',
    'mkdir' : 'Creates a new directory in the current directory of the fileserver.\nUsage : mkdir <name>',
    'lmkdir' : 'Creates a new directory in the current directory of the client.\nUsage : lmkdir <name>',
    'download' : 'Transfers a file/directory from the current directory of the fileserver to the current directory of the client.\nUsage : download <filename>/<directory>',
    'upload' : 'Transfers a file/directory from the current directory of the client to the current directory of the fileserver.\nUsage : upload <filename>/<directory>',
}

MAX_BUFFER_SIZE=8192
END="END"

def hit_server(socket, tokens):
    socket.sendall(" ".join(tokens))

def handle_help(tokens):
    """Displays informations about commands"""
    if len(tokens) > 2:
        command=tokens[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    if len(tokens) == 1:
        print("All available commands :")
        for cmd in commands:
            print(f"- {cmd}")
    else:
        command_to_desc=tokens[1].lower()
        description=commands.get(command_to_desc)
        if description:
            print(f"Command '{command_to_desc}' : {description}")
        else:
            print(f"Command '{command_to_desc}' not found")


def handle_cd(tokens):
    if check_command_validity(tokens,2):
        hit_server(tokens)

def handle_list(tokens):
    if check_command_validity(tokens,1):
        hit_server(tokens)

def handle_mkdir(tokens):
    if check_command_validity(tokens,2):
        hit_server(tokens)

def handle_pwd(tokens):
    if check_command_validity(tokens,1):
        hit_server(tokens)

def handle_download(tokens, client_socket):
    if check_command_validity(tokens, 2):
        filename = tokens[1]
        try:
            # Envoyer la requête de téléchargement au serveur
            client_socket.sendall(f"download {filename}".encode())
            
            # Recevoir le fichier du serveur
            with open(filename, "wb") as file:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    print(f"Received {len(data)} bytes")
            print(f"File '{filename}' downloaded successfully.")
        except Exception as e:
            print(f"Error during download: {e}")


def send_file(filepath, client_socket):
    client_socket.settimeout(5)
    attempt=0
    while attempt<3 :
        try:
            with open(filepath, "rb") as file:
                while True:
                    data = file.read(8192)
                    if not data:
                        break
                    client_socket.sendall(data)
                    print(f"Sent {len(data)} bytes")
            client_socket.sendall(END.encode())
            print(f"File '{filepath}' sent successfully.")
            return True
        except socket.timeout:
            print(f"Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except FileNotFoundError:
            print(f"File '{filepath}' not found.")
        except Exception as e:
            print(f"Error while sending file: {e}")
    return False

def send_directory(filepath,client_socket):
    


def handle_upload(tokens, client_socket):
    client_socket.settimeout(5)
    if check_command_validity(tokens, 2):
        path = tokens[1]
        if not os.path.exists(path):
            print(f"Path {path} does not exist.")
            return
        attempt=0
        while attempt<3:
            try:
                # Envoyer d'abord la commande d'upload au serveur
                resp=""
                while resp!="ACK" :
                    client_socket.sendall(f"upload {path}".encode())
                    resp=client_socket.recv(8192).decode("utf-8").strip()
                    if resp != "ACK":
                        print("Error while sending command")
                        print("Retrying")
                # Ensuite, envoyer le fichier après la commande
                if os.path.isdir(path):
                    return send_directory(path, client_socket)
                else:
                    return send_file(path, client_socket)
            except socket.timeout:
                print(f"Attempt {attempt + 1}: Timeout occurred while sending data")
                attempt+=1
            except Exception as e:
                print(f"Error during upload: {e}")
            return False


def check_command_validity(tokens:str, expected_length:int) -> bool:
    if len(tokens) is not expected_length:
        command=tokens[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command).split(':')[1]}")
        return False
    return True

def handle_lcd(tokens, _):
    if not check_command_validity(tokens,2):
        return
    path=tokens[1]
    if not os.path.isdir(path):
        print(f"Path {path} does not exists.")
        return
    try:
        os.chdir(path)
    except PermissionError:
        print(f"You do not have permission to access {path}")
    except Exception as e:
        print(f"Error acceding the directory : {e}")

def handle_llist(tokens, _):
    if not check_command_validity(tokens,1):
        return
    list=os.listdir()
    for file in list:
        print(file)

def handle_lmkdir(tokens):
    if not check_command_validity(tokens,2):
        return
    path=tokens[1].lower()
    if os.path.exists(path):
        print(f"{path} already exists")
        return
    try:
        os.mkdir(path)
    except FileNotFoundError:
        print(f"{path} is incorrect")

def handle_lpwd(tokens):
    if not check_command_validity(tokens,1):
        return
    print(os.getcwd())
    
# Dictionary to store the handler of the commands  

command_map = {
    'help' : handle_help,
    'cd' : handle_cd,
    'list' : handle_list,
    'mkdir' : handle_mkdir,
    'pwd' : handle_pwd,
    'download' : handle_download,
    'upload' : handle_upload,
    'lcd' : handle_lcd,
    'llist' : handle_llist,
    'lmkdir' : handle_lmkdir,
    'lpwd' : handle_lpwd
}