import os


#Dictionary to store commands (mostly used for 'help')
commands = {
    'help' : 'Display the list of all commmands or provides more detail on a specific command.\nUsage : help [<command>]',
    'cd' : 'Access the given directory in the current directory of the fileserver.\nUsage : cd <directory>',
    'list' : 'List all the files in the current directory of the fileserver.\nUsage : list',
    'mkdir' : 'Create a new directory in the current directory of the fileserver.\nUsage : mkdir <name>',
    'pwd' : 'Return the name of the current directory of the fileserver.\nUsage : pwd',
    'download' : 'Transfer a file/directory from the current directory of the fileserver to the current directory of the client.\nUsage : download <filename>/<directory>',
    'upload' : 'Transfer a file/directory from the current directory of the client to the current directory of the fileserver.\nUsage : upload <filename>/<directory>',
    'lcd' : 'Access the given directory in the current directory of the client.\nUsage : lcd <directory',
    'llist' : 'List all the files in the current directory of the client.\nUsage : llist',
    'lmkdir' : 'Create a new directory in the current directory of the client.\nUsage : lmkdir <name>',
    'lpwd' : 'return the name of the current directory of the client.\nUsage : lpwd'
}

def send_receive_data():
    return

def handle_help(parts):
    """Display informations about commands"""
    if len(parts)>2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    if len(parts)==1 :
        print("All available commands :")
        for cmd in commands :
            print(f"- {cmd}")
    else :
        command_to_desc=parts[1].lower()
        description=commands.get(command_to_desc)
        if description:
            print(f"Command '{command_to_desc}' : {description}")
        else :
            print(f"Command '{command_to_desc}' not found")



def handle_cd(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    send_receive_data(parts)

    

def handle_list(parts):
    if len(parts)!=1:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    send_receive_data(parts)

def handle_mkdir(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    send_receive_data(parts)

def handle_pwd(parts):
    if len(parts)!=1:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    send_receive_data(parts)

def handle_download(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    send_receive_data(parts)

def handle_upload(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    path=parts[1]
    if not os.path.exists(path):
        print(f"Path {path} does not exists.")
        return
    
    send_receive_data(parts)




def handle_lcd(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    path=parts[1]
    if not os.path.isdir(path):
        print(f"Path {path} does not exists.")
        return
    try:
        os.chdir(path)
    except PermissionError:
        print(f"You do not have permission to access {path}")
    except Exception as e:
        print(f"Error acceding the directory : {e}")

def handle_llist(parts):
    if len(parts)!=1:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    list=os.listdir()
    
    for file in list:
        print(file)
    
    

def handle_lmkdir(parts):
    if len(parts)!=2:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    

def handle_lpwd(parts):
    if len(parts)!=1:
        command=parts[0].lower()
        print(f"Wrong number of argument.\n{command} : {commands.get(command)}")
        return
    


#Dictionary to store the handler of the commands  
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