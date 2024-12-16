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
RESET = "\033[0m"
LIGHT_PURPLE = "\033[95m"
LIGHT_GREEN = "\033[92m"
LIGHT_BLUE = "\033[94m"
LIGHT_YELLOW = "\033[93m"
LIGHT_RED = "\033[91m"

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
        print(LIGHT_RED + f"Wrong number of argument.\n{command} : {commands.get(command)}" + RESET)
        return
    if len(tokens) == 1:
        print("All available commands :")
        for cmd in commands:
            print(f"- {cmd}")
    else:
        command_to_desc = tokens[1].lower()
        description = commands.get(command_to_desc)
        if description:
            print(LIGHT_GREEN + f"Command '{command_to_desc}' : {RESET} {LIGHT_BLUE} {description} {RESET}")
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
            print(LIGHT_YELLOW + f"[-] Attempt {attempt + 1}: Timeout occurred while sending data" + RESET)
            attempt+=1
        except Exception as e:
            print(LIGHT_RED + f"[-] Error while sending request: {e}" + RESET)
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
                global session_cursor 
                session_cursor = resp
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
            if 'session_cursor' in globals():
                print(LIGHT_GREEN + f"=== Files in {session_cursor} : === " + RESET)
            while True:
                data = client_socket.recv(MAX_BUFFER_SIZE).decode().strip()
                if data=="NACK":
                    attempt+=1
                    print(LIGHT_YELLOW + "Server responded with NACK, resending request" + RESET)
                    continue
                if compare_bits(data):
                    client_socket.sendall(b"ACK")
                    print(LIGHT_PURPLE + f"{data[:-3]}" + RESET)
                    return
                print(LIGHT_PURPLE + f"{data}" + RESET)
        except socket.timeout:
            print(LIGHT_RED + "[-] Timeout occurred while receiving data" + RESET)
            attempt+=1
        except Exception as e:
            print(LIGHT_RED + f"[-] Error receiving list: {e}" + RESET)
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
                print(LIGHT_GREEN + f"[+] Successfully created {tokens[1]}" + RESET)
                return True
            if resp == "alr_exists":
                print(LIGHT_RED + f"[-] Folder {tokens[1]} already exists !" + RESET)
                return False
        except socket.timeout:
            attempt+=1
            print(LIGHT_RED + "[-] Timeout occured" + RESET)
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
                print(LIGHT_YELLOW + f"[+] Receiving file: {save_path} + RESET")
                while True:
                    data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
                    if compare_bits(data):
                        file.write(data[:-3].encode())
                        sock.sendall(b'ACK')
                        print(LIGHT_GREEN + f"[-] Successfully downloaded {save_path}" + RESET)
                        return True
                    file.write(data.encode())
        except socket.timeout:
            attempt+=1
            print(LIGHT_YELLOW + "Timeout occured while waiting for data" + RESET)
            sock.sendall(b'NACK')
        except Exception as e:
            print(LIGHT_RED + f"[-] Error while creating file: {e}" + RESET)
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
    print(LIGHT_GREEN + f"[+] Receiving directory: {base_path}" + RESET)
    os.makedirs(base_path, exist_ok=True)
    while True:
        try:
            data = sock.recv(MAX_BUFFER_SIZE).decode().strip()
            if compare_bits(data):
                sock.sendall(b'ACK')
                return True
            # The server sends back "file <filename>" or "dir <dirname>"
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
            print(LIGHT_RED + f"[-] Error while trying to download : {e}" + RESET)
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
                print("Received NACK from server, resending the message." if attempt<3 else LIGHT_RED + "[-] Could not send message to server." + RESET)
                continue
            return resp=="ACK"
        except socket.timeout:
            print(LIGHT_YELLOW + f"Attempt {attempt + 1}: Timeout occurred while sending data" + RESET)
            attempt+=1
        except Exception as e:
            print(LIGHT_RED + f"Error while sending request: {e}" + RESET)
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
                    print(LIGHT_YELLOW + f"Sent {len(data)} bytes" + RESET)
            # Send END signal after sending the file
            client_socket.sendall(END.encode())
            resp=client_socket.recv(MAX_BUFFER_SIZE).decode()
            if resp == "NACK":
                attempt+=1
                continue
            print(LIGHT_GREEN + f"File '{filepath}' sent successfully." + RESET)
            return True
        except socket.timeout:
            print(LIGHT_YELLOW + f"Attempt {attempt + 1}: Timeout occurred while sending data" + RESET)
            attempt+=1
        except FileNotFoundError:
            print(LIGHT_RED + f"File '{filepath}' not found." + RESET)
            return False
        except Exception as e:
            print(LIGHT_RED + f"Error while sending file: {e}" + RESET)
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
                    print(LIGHT_RED + f"[-] {file} could not be uploaded" + RESET)
                else:
                    print(LIGHT_GREEN + f"[+] {file} successfully uploaded" + RESET)
            # Send END after sending directory contents
            client_socket.sendall(END.encode())
            resp=client_socket.recv(1024).decode()
        except socket.timeout:
            print(LIGHT_RED + "Timeout" + RESET)
            attempt+=1
        except Exception as e:
            print(LIGHT_RED + f"Error : {e}" + RESET)
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
            print(LIGHT_RED + f"Path {path} does not exist." + RESET)
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
                        print(LIGHT_RED + "Error while sending command" + RESET)
                        print("Retrying")
                # Then send the actual file or directory
                if os.path.isdir(path):
                    return send_directory(path, client_socket)
                else:
                    return send_file(path, client_socket)
            except socket.timeout:
                print(LIGHT_RED + f"Attempt {attempt + 1}: Timeout occurred while sending data" + RESET)
                attempt+=1
            except Exception as e:
                print(LIGHT_RED + f"Error during upload: {e}" + RESET)
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
        print(LIGHT_RED + f"Wrong number of argument.\n{command} : {commands.get(command).split(':')[1]}" + RESET)
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
        print(LIGHT_RED + f"Path {path} does not exists." + RESET)
        return
    try:
        os.chdir(path)
    except PermissionError:
        print(LIGHT_RED + f"You do not have permission to access {path}" + RESET)
    except Exception as e:
        print(LIGHT_RED + f"Error accessing the directory : {e}" + RESET)

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
    print(LIGHT_YELLOW + f"===== Files in {os.getcwd()} =====" + RESET)
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
        print(LIGHT_RED + f"{path} already exists" + RESET)
        return
    try:
        os.mkdir(path)
    except FileNotFoundError:
        print(LIGHT_RED + f"{path} is incorrect" + RESET)

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
    print(LIGHT_YELLOW + f"{os.getcwd()}" + RESET)
    
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
