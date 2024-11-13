import os

# Dictionary to store commands (mostly used for 'help')
commands = {
    'help' : 'Displays the list of all commmands or provides more detail on a specific command.\nUsage : help [<command>]',
    'list' : 'Lists all the files in the current directory of the fileserver.\nUsage : list',
    'llist' : 'Lists all the files in the current directory of the client.\nUsage : llist',
    'pwd' : 'Returns the name of the current directory of the fileserver.\nUsage : pwd',
    'lpwd' : 'Returns the name of the current directory of the client.\nUsage : lpwd',
    'cd' : 'Accesses the given directory in the current directory of the fileserver.\nUsage : cd <directory>',
    'lcd' : 'Accesses the given directory in the current directory of the client.\nUsage : lcd <directory',
    'mkdir' : 'Creates a new directory in the current directory of the fileserver.\nUsage : mkdir <name>',
    'lmkdir' : 'Creates a new directory in the current directory of the client.\nUsage : lmkdir <name>',
    'download' : 'Transfers a file/directory from the current directory of the fileserver to the current directory of the client.\nUsage : download <filename>/<directory>',
    'upload' : 'Transfers a file/directory from the current directory of the client to the current directory of the fileserver.\nUsage : upload <filename>/<directory>',
}

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

def handle_download(tokens):
    if check_command_validity(tokens,2):
        hit_server(tokens)

def handle_upload(tokens):
    if check_command_validity(tokens,2):
        path=tokens[1]
    if not os.path.exists(path):
        print(f"Path {path} does not exists.")
        return
    hit_server(tokens)

def check_command_validity(tokens:str, expected_length:int) -> bool:
    if len(tokens) is not expected_length:
        command=tokens[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command).split()[1]}")
        return False
    return True

def handle_lcd(tokens):
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

def handle_llist(tokens):
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