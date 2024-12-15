import os
import socket

# Dictionary of available commands and their descriptions.
# Used primarily for the 'help' command to provide usage instructions.
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
    """
    Display information about available commands or a specific command.

    Args:
        tokens (list): The list of command tokens. 
                       If `tokens` contains only 'help', it lists all commands.
                       If `tokens` contains 'help <command>', it displays details for that command.

    Returns:
        None
    """
    if len(tokens) > 2:
        command = tokens[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    if len(tokens) == 1:
        print("All available commands :")
        for cmd in commands:
            print(f"- {cmd}")
    else:
        command_to_desc = tokens[1].lower()
        description = commands.get(command_to_desc)
        if description:
            print(f"Command '{command_to_desc}' : {description}")
        else:
            print(f"Command '{command_to_desc}' not found")

def handle_cd(tokens, client_socket):
    """
    Change the current directory on the fileserver.

    Args:
        tokens (list): tokens[0] should be 'cd', tokens[1] the directory to change to.
        client_socket (socket.socket): The client socket connected to the server.

    Returns:
        bool: True on success, False on failure.
    """
    if not check_command_validity(tokens,2):
        return False
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
                # If unexpected response, retry
                attempt +=1
        except socket.timeout:
            print(f"[-] Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except Exception as e:
            print(f"[-] Error while sending request: {e}")
            return False
    return False

def handle_pwd(tokens, client_socket):
    """
    Print the current directory on the fileserver.

    Args:
        tokens (list): tokens[0] should be 'pwd'.
        client_socket (socket.socket): The client socket connected to the server.

    Returns:
        bool: True on success, False otherwise.
    """
    if not check_command_validity(tokens,1):
        return False
    client_socket.settimeout(1)
    attempt = 0
    while attempt<3:
        try:
            client_socket.sendall("pwd".encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp=="no_session":
                attempt+=1
                print("[!] Received error from server, resending the message." if attempt<3 else "[-] Could not send message to server.")
                continue
            else:
                print(resp)
                return True
        except socket.timeout:
            print(f"[-] Attempt {attempt + 1}: Timeout occurred while sending data")
            attempt+=1
        except Exception as e:
            print(f"[-] Error while sending request: {e}")
    return False

def handle_list(tokens, client_socket):
    """
    List files in the current directory on the fileserver by sending a command to the server.

    Args:
        tokens (list): tokens[0] should be 'list'.

    Returns:
        None
    """
    if not check_command_validity(tokens, 1):
        return
    client_socket.settimeout(5)
    attempt=0
    while attempt<3:
        try:
            client_socket.sendall("list".encode())
            print("Files on server:")
            while True:
                data = client_socket.recv(MAX_BUFFER_SIZE).decode().strip()
                if data=="NACK":
                    attempt+=1
                    print("Server responded with NACK, resending request")
                    continue
                if compare_bits(data):
                    client_socket.sendall(b"ACK")
                    print(data[:-3])
                    return
                print(data)
        except socket.timeout:
            print("[-] Timeout occurred while receiving data")
            attempt+=1
        except Exception as e:
            print(f"[-] Error receiving list: {e}")
            attempt+=1

def handle_mkdir(tokens, sock):
    """
    Create a new directory on the fileserver.

    Args:
        tokens (list): tokens[0] should be 'mkdir', tokens[1] the directory name.

    Returns:
        None
    """
    if not check_command_validity(tokens,2):
        return
    sock.settimeout(1)
    attempt=0
    while attempt<3:
        try:
            sock.sendall(f"mkdir {tokens[1]}".encode())
            resp = sock.recv(MAX_BUFFER_SIZE).decode().strip()
            if resp == "ACK":
                print(f"[+] Successfully created {tokens[1]}")
                return True
            if resp == "alr_exists":
                print(f"[-] Folder {tokens[1]} already exists !")
                return False
        except socket.timeout:
            attempt+=1
            print("[-] Timeout occured")
    return False

def compare_bits(data):
    """
    Check if the last 3 characters of data match the END signal.

    Args:
        data (str): The data to check.

    Returns:
        bool: True if data ends with 'END', otherwise False.
    """
    return data[-3:] == END

def receive_file(sock, save_path):
    """
    Receive a file from the server and save it locally.

    Args:
        sock (socket.socket): The connected socket.
        save_path (str): The path where the received file will be saved.

    Returns:
        bool: True if file received successfully, False otherwise.
    """
    sock.settimeout(5)
    attempt=0
    while attempt<3:
        try:
            with open(save_path, 'wb') as file:
                print(f"[+] Receiving file: {save_path}")
                while True:
                    data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
                    if compare_bits(data):
                        # Write remaining data (excluding END)
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
    """
    Recursively receive a directory and its contents from the server.

    Args:
        sock (socket.socket): The connected socket.
        base_path (str): The local base directory where the received directory will be created.

    Returns:
        bool: True on success, False otherwise.
    """
    print(f"[+] Receiving directory: {base_path}")
    os.makedirs(base_path, exist_ok=True)
    while True:
        try:
            data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
            if compare_bits(data):
                sock.sendall(b'ACK')
                return True
            # The server sends "file <filename>" or "dir <dirname>"
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
            return False

def send_upload_type(message,client_socket):
    """
    Send the initial upload type message (file or directory) to the server and wait for ACK.

    Args:
        message (str): The message describing the upload type, e.g. "file <path>" or "dir <path>".
        client_socket (socket.socket): The connected client socket.

    Returns:
        bool: True if ACK is received, False otherwise.
    """
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
    """
    Send a file to the server.

    Args:
        filepath (str): The local file path to send.
        client_socket (socket.socket): The connected client socket.

    Returns:
        bool: True if file is sent successfully, False otherwise.
    """
    if not send_upload_type(f"file {filepath}",client_socket):
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
            # Send END signal after sending the file
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
            return False
        except Exception as e:
            print(f"Error while sending file: {e}")
            return False
    return False

def send_directory(dir_path,client_socket):
    """
    Send a directory and its contents to the server, recursively.

    Args:
        dir_path (str): The local directory path to send.
        client_socket (socket.socket): The connected client socket.

    Returns:
        bool: True if directory is sent successfully, False otherwise.
    """
    attempt=0
    resp="NACK"
    client_socket.settimeout(10)
    while resp=="NACK" and attempt < 3:
        try:
            if not send_upload_type(f"dir {dir_path}",client_socket):
                return False
            files=os.listdir(dir_path)
            for file in files:
                full_path = os.path.join(dir_path, file)
                if os.path.isdir(full_path):
                    send_directory(full_path,client_socket)
                    continue
                if not send_file(full_path,client_socket):
                    print(f"{file} could not be uploaded")
                else:
                    print(f"{file} successfully uploaded")
            # Send END after sending directory contents
            client_socket.sendall(END.encode())
            resp=client_socket.recv(1024).decode()
        except socket.timeout:
            print("Timeout")
            attempt+=1
        except Exception as e:
            print(f"Error : {e}")
    if attempt==3:
        return False
    return True

def handle_upload(tokens, client_socket):
    """
    Handle the upload command to send a file or directory from the client to the server.

    Args:
        tokens (list): tokens[0] = 'upload', tokens[1] = path of file/directory to upload.
        client_socket (socket.socket): Connected client socket.

    Returns:
        bool: True if upload succeeds, False otherwise.
    """
    client_socket.settimeout(115)
    if check_command_validity(tokens, 2):
        path = tokens[1]
        if not os.path.exists(path):
            print(f"Path {path} does not exist.")
            return False
        attempt=0
        while attempt<3:
            try:
                # Send the upload command first
                resp=""
                while resp!="ACK" :
                    client_socket.sendall(f"upload {path}".encode())
                    resp=client_socket.recv(8192).decode("utf-8").strip()
                    if resp == "NACK":
                        print("Error while sending command")
                        print("Retrying")
                # Then send the actual file or directory
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
    Handle the 'download' command, receiving a file or directory from the server.

    Args:
        args (list): tokens[0] = 'download', tokens[1] = remote filename/directory to download.
        sock (socket.socket): Connected client socket.

    Returns:
        None
    """
    attempt = 0
    response = ''
    if not check_command_validity(args, 2):
        return
    command = f"download {args[1]}"
    while attempt < 3 and response not in ('file', 'dir'):
        sock.sendall(command.encode())
        response = sock.recv(MAX_BUFFER_SIZE).decode()
        if response.strip() == "NACK":
            attempt += 1
            print("[-] Server: File or directory not found.")
    if response == 'file':
        receive_file(sock, args[1])
    elif response == 'dir':
        receive_directory(sock,args[1])

def check_command_validity(tokens:str, expected_length:int) -> bool:
    """
    Check if a command has the expected number of arguments.

    Args:
        tokens (list): The command arguments.
        expected_length (int): The expected length of tokens.

    Returns:
        bool: True if valid, False otherwise.
    """
    if len(tokens) != expected_length:
        command=tokens[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command).split(':')[1]}")
        return False
    return True

def handle_lcd(tokens, _):
    """
    Change the local current directory (on the client machine).

    Args:
        tokens (list): tokens[0] = 'lcd', tokens[1] = local directory to change to.
        _ : Unused parameter (client_socket).

    Returns:
        None
    """
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
        print(f"Error accessing the directory : {e}")

def handle_llist(tokens, _):
    """
    List files in the current local directory (on the client machine).

    Args:
        tokens (list): tokens[0] = 'llist'.
        _ : Unused parameter (client_socket).

    Returns:
        None
    """
    if not check_command_validity(tokens,1):
        return
    listing=os.listdir()
    for file in listing:
        print(file)

def handle_lmkdir(tokens, _):
    """
    Create a new directory in the local current directory (on the client machine).

    Args:
        tokens (list): tokens[0] = 'lmkdir', tokens[1] = directory name.
        _ : Unused parameter (client_socket).

    Returns:
        None
    """
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
    """
    Print the local current working directory (on the client machine).

    Args:
        tokens (list): tokens[0] = 'lpwd'.
        _ : Unused parameter (client_socket).

    Returns:
        None
    """
    if not check_command_validity(tokens,1):
        return
    print(os.getcwd())
    
# Dictionary mapping commands to their respective handler functions
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
