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

def handle_cd(tokens, client_socket):
    if not check_command_validity(tokens,2):
        return
    client_socket.settimeout(1)
    attempt = 0
    while attempt<3:
        try:
            client_socket.sendall(f"cd {tokens[1]}".encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp.startswith("[-]"):
                print(f"{resp}")
                return False
            elif resp=="ACK":
                return True
            else:
                attempt +=1
                print(f"",end="" if attempt<3 else "[-] Could not send message to server.")
        except socket.timeout:
            print(f"[-] Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except Exception as e:
            print(f"[-] Error while sending request: {e}")
    return False

def handle_pwd(tokens, client_socket):
    if not check_command_validity(tokens,1):
        return
    client_socket.settimeout(1)
    attempt = 0
    while attempt<3:
        try:
            client_socket.sendall(f"pwd".encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp=="no_session":
                attempt+=1
                print("[!] Received error from server, resending the message." if attempt<3 else "[-] Could not send message to server.")
                continue
            else:
                print(resp)
                return True;
        except socket.timeout:
            print(f"[-] Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except Exception as e:
            print(f"[-] Error while sending request: {e}")
    return False

def handle_list(tokens):
    if check_command_validity(tokens,1):
        hit_server(tokens)

def handle_mkdir(tokens):
    if check_command_validity(tokens,2):
        hit_server(tokens)
   
def compare_bits(data):
    return data[-3:] == END

def receive_file(sock, save_path):
    """ Reçoit un fichier et l'enregistre à save_path """
    sock.settimeout(5)
    attempt=0
    while attempt<3:
        try:
            with open(save_path, 'wb') as file:
                print(f"[+] Receiving file: {save_path}")
                while True:
                    data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
                    if compare_bits(data):
                        file.write(data[:-3].encode())
                        sock.sendall(b'ACK')
                        print(f"Successfully downloaded {save_path}")
                        return True
                    file.write(data.encode())

        except socket.timeout:
            attempt+=1
            print("Timeout occured while waiting for data")
            sock.sendall(b'NACK')
        except Exception as e:
            print(f"Error while creating file: {e}")
            attempt+=1
            if attempt <3 : sock.sendall(b'NACK')
    return False

def receive_directory(sock, base_path):
    """ Reçoit un répertoire et son contenu récursivement """
    print(f"[+] Receiving directory: {base_path}")
    os.makedirs(base_path, exist_ok=True)
    while True:
        try:
            data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
            if compare_bits(data):
                sock.sendall(b'ACK')
                return True
            print(data)
            if data.startswith("file"):
                sock.sendall(b'ACK')
                _, filename = data.split(" ", 1)
                file_path = os.path.join(base_path, filename.strip())
                receive_file(sock, file_path)
            elif data.startswith("dir"):
                sock.sendall(b'ACK')
                _, dirname = data.split(" ", 1)
                new_dir_path = os.path.join(base_path, dirname.strip())
                receive_directory(sock, new_dir_path)
        except Exception as e:
            print(f"Error while trying to download : {e}")
            sock.sendall(b"NACK")
            return

def send_upload_type(message,client_socket):
    client_socket.settimeout(10)
    attempt=0
    while attempt<3:
        try:
            client_socket.sendall(message.encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp=="NACK":
                attempt+=1
                print("Received NACK from server, resending the message." if attempt<3 else "Could not send message to server.")
                continue
            return resp=="ACK"
        except socket.timeout:
            print(f"Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except Exception as e:
            print(f"Error while sending request: {e}")
    return False

def send_file(filepath, client_socket):
    if send_upload_type(f"file {filepath}",client_socket) is False:
        return False
    client_socket.settimeout(10)
    attempt=0
    while attempt<3 :
        try:
            with open(filepath, "rb") as file:
                while True:
                    data = file.read(MAX_BUFFER_SIZE)
                    if not data:
                        break
                    client_socket.sendall(data)
                    print(f"Sent {len(data)} bytes")
            client_socket.sendall(END.encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp == "NACK":
                attempt+=1
                continue
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

def send_directory(dir_path,client_socket):
    attempt=0
    resp="NACK"
    client_socket.settimeout(10)
    while resp=="NACK" and attempt < 3:
        try :
            if send_upload_type(f"dir {dir_path}",client_socket) is False:
                return
            files=os.listdir(dir_path)
            for file in files:
                if os.path.isdir(dir_path+"/"+file):
                    send_directory(dir_path+"/"+file,client_socket)
                    continue
                if send_file(dir_path+"/"+file,client_socket) is False:
                    print(f"{file} could not be uploaded")
                else:
                    print(f"{file} successfully uploaded")
            client_socket.sendall(END.encode())
            resp=client_socket.recv(1024).decode()
        except socket.timeout :
            print("Timeout")
            attempt+=1
        except Exception as e:
            print(f"Error : {e}")
    if attempt==3:
        return False
    return True


def handle_upload(tokens, client_socket):
    client_socket.settimeout(115)
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
                    if resp == "NACK":
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


def handle_download(args, sock):
    """
    Gère la commande 'download' en appelant les fonctions appropriées pour
    recevoir un fichier ou un répertoire.
    Args:
        sock : La socket connectée au serveur.
        args : Les arguments de la commande (chemin distant, chemin local).
    """
    attempt = 0
    response = ''
    if not check_command_validity(args, 2):
        return
    command = f"download {args[1]}"
    while attempt < 3 and response != 'file' and response != 'dir':
        sock.sendall(command.encode())  # Envoi de la commande au serveur
        response = sock.recv(MAX_BUFFER_SIZE).decode()
        if response.strip() == "NACK":
            attempt += 1
            print("[-] Server: File or directory not found.")
    if response == 'file':
        receive_file(sock, args[1])
    elif response == 'dir':
        receive_directory(sock,args[1])


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

def handle_lmkdir(tokens, _):
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

def handle_lpwd(tokens, _):
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