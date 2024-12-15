/**
 * @file server.c
 * @brief Server implementation file.
 *
 * This file implements the server setup, event loop handling, and
 * client request management including file and directory handling.
 *
 * It depends on "../include/server.h" for type definitions and function prototypes.
 */

#include "../include/server.h"

/**
 * @var int num_clients
 * @brief The number of currently connected clients.
 *
 * This variable tracks how many clients are currently connected to the server.
 * @warning DO NOT MODIFY THIS VARIABLE, IT WILL BREAK EVERYTHING.
 */
int num_clients = 0; //DO NOT MODIFY THAT PLEASE IT WILL BREAK EVERYTHING

/**
 * @var client_session clients[MAX_CLIENT]
 * @brief Array of client sessions.
 *
 * This array holds the sessions for up to MAX_CLIENT clients.
 */
client_session clients[MAX_CLIENT];

/**
 * @brief Sets up the storage directory.
 *
 * Checks if the storage directory exists. If it doesn't exist, creates the directory
 * with permissions set to 0700. If the directory already exists, prints a message indicating its existence.
 *
 * @return None
 */
void setup_storage_dir() {
    struct stat st = {0};
    if (stat(STORAGE_DIR, &st) != ERR) {
        printf("[!] Storage directory already exists at : %s\n", STORAGE_DIR);
        return;
    }
    if (mkdir(STORAGE_DIR, 0700) == ERR) err(Could not setup the storage directory, 5)
    printf("Storage directory created at : %s\n", STORAGE_DIR);
}

/**
 * @brief Initializes the server.
 *
 * This function sets up the server's storage directory,
 * creates a socket for the server (both TCP and UDP), and initializes
 * the server structure with given interface and port.
 *
 * @param server A pointer to the Server structure to be initialized.
 * @param port The port number the server will listen on.
 * @param interface The network interface name the server binds to.
 * @return None
 */
void init(Server* server, int port, const char* interface) {
    printf("Setting up the storage directory...\n");
    setup_storage_dir();
    init_with_capacity(&server->buff, MAX_BUFFER_SIZE);
    num_clients=0;
    printf("Setting up the socket...\n");
    if ((server->tcp_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) 
        err(Could not initialize the server socket, 4);

    int opt = 1;
    setsockopt(server->tcp_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    printf("Setting up server address...\n");
    server->serv_addr.sin_family = AF_INET;
    if ((server->serv_addr.sin_addr.s_addr = get_local_ip_of_interface(interface)) == ERR) 
        err(Could not get local ip of the interface, 12);

    server->serv_addr.sin_port = htons(port);

    printf("Binding the socket and the address...\n");
    if (bind(server->tcp_fd, (struct sockaddr*)&server->serv_addr, sizeof(server->serv_addr)) == ERR)  
        err(Could not bind the socket to the local address, 7);
    if (listen(server->tcp_fd, MAX_CLIENT) == ERR) 
        err(Could not set the socket to listen, 8);

    printf("Listening...\n");

    if ((server->udp_fd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) 
        err("Could not create UDP socket", 13);


    int broadcast_enable = 1;
    if (setsockopt(server->udp_fd, SOL_SOCKET, SO_BROADCAST, &broadcast_enable, sizeof(broadcast_enable)) < 0) {
        perror("Setting UDP socket option failed");
        exit(1);
    }

    struct sockaddr_in udp_addr;
    memset(&udp_addr, 0, sizeof(udp_addr));
    udp_addr.sin_family = AF_INET;
    udp_addr.sin_addr.s_addr = INADDR_ANY;
    udp_addr.sin_port = htons(BROADCAST_PORT);

    if (bind(server->udp_fd, (struct sockaddr*)&udp_addr, sizeof(udp_addr)) < 0) {
        perror("Could not bind UDP socket");
        exit(1);
    }

    printf("UDP socket bound for broadcast discovery on port %d\n", BROADCAST_PORT);
}

/**
 * @brief Retrieve a client session based on the socket descriptor.
 *
 * @param socket The socket descriptor of the client.
 * @return A pointer to the client_session or NULL if not found.
 */
client_session* get_client_session_by_socket(int socket) {
    printf("List of clients : \n");
    for (int i = 0; i < num_clients; i++) {
        printf("> %d \n", clients[i].socket);
        if (clients[i].socket == socket) {
            return &clients[i];
        }
    }
    return NULL;  
}

/**
 * @brief Callback function triggered upon a new client connection.
 *
 * Accepts a new client connection, initializes a client_session for it, and adds
 * a new event to read data from this client.
 *
 * @param fd The listening socket file descriptor.
 * @param events The event flags.
 * @param arg A pointer to the Server structure.
 */
void on_accept(evutil_socket_t fd, short events, void* arg) {
    Server* server = (Server*)arg;
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_fd = accept(fd, (struct sockaddr*)&client_addr, &client_len);
    if (client_fd < 0) {
        perror("Error accepting client connection");
        return;
    }

    printf("[!] New client connected\n");
    clients[num_clients].socket = client_fd;
    strcpy(clients[num_clients].current_dir, STORAGE_DIR);
    num_clients++;
    struct event* client_event = event_new(server->base, client_fd, EV_READ | EV_PERSIST, on_client_data, server);
    event_add(client_event, NULL);
}

/**
 * @brief Writes data received from the client into a file.
 *
 * This function receives data chunks from the client until it encounters
 * an end signal or times out. It then writes those chunks into the specified file.
 *
 * @param client_fd The client's file descriptor.
 * @param filepath The path to the file on the server where data should be written.
 * @return int Returns 1 on success or ERR on failure.
 */
int write_file(int client_fd,char *filepath){
    size_t bytes_read;
    char buffer[MAX_BUFFER_SIZE];
    struct timeval timeout = {5, 0};
    if (setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
        perror("Could not set socket timeout");
        return ERR;
    }
    FILE* file = fopen(filepath, "wb");
    if (!file) {
        perror("Could not open file to write");
        return ERR;
    }
    int attempt=0;
    while (attempt<3) {
        bytes_read = recv(client_fd, buffer, MAX_BUFFER_SIZE, 0);
        if (bytes_read == 0) {
            printf("Client closed the connection\n");
            close(client_fd);
            break;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            errno = 0;
            printf("Timeout occurred, no data received\n");
            send(client_fd,NACK,strlen(NACK),0);
            attempt++;
            continue;
        }


        if (check_end_signal(buffer, bytes_read)) {
            if (bytes_read - LEN_END > 0) {
                fwrite(buffer, 1, bytes_read - LEN_END, file);
                printf("Wrote %ld bytes to file\n", bytes_read - LEN_END);
            }
            printf("Received end of transmission signal\n");
            send(client_fd,ACK,strlen(ACK),0);
            break;
        }
        size_t bytes_written = fwrite(buffer, 1, bytes_read, file);
        if (bytes_written != bytes_read) {
            perror("Error writing to file");
            break;
        }
        printf("Wrote %ld bytes to file\n", bytes_read);
    }
    fclose(file);
    return 1;
}

/**
 * @brief Recursively receives directories and their contents from the client and writes them to the server storage.
 *
 * If the specified directory does not exist, it creates it. For each file or directory
 * received, it writes the file or recursively processes the sub-directory.
 *
 * @param client_fd The client's file descriptor.
 * @param dir_path The directory path on the server where data should be written.
 * @return int Returns 1 on success or ERR on failure.
 */
int write_directory(int client_fd,char *dir_path){
    struct stat st ={0};
    size_t bytes_read=0;
    char buffer[MAX_BUFFER_SIZE]="";
    if(stat(dir_path,&st)==-1){
        mkdir(dir_path, 0777);
    }
    char *newpath=calloc(2048,sizeof(char));
    char *filedir=calloc(2048,sizeof(char));
    struct timeval timeout={5,0};
    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    int attempt=0;
    while (attempt<3) {
        bytes_read = recv(client_fd, buffer, MAX_BUFFER_SIZE, 0);
        if (bytes_read==0){
            printf("Client closed the connection\n");
            close(client_fd);
            break; 
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            errno = 0;
            printf("[-] Timeout occurred, no data received\n");
            send(client_fd,NACK,strlen(NACK),0);
            attempt++;
            continue;
        }

        if (check_end_signal(buffer, bytes_read)) {
            printf("Received end of transmission signal\n");
            send(client_fd, ACK, strlen(ACK), 0);
            break;
        }
        int dir = is_dir(buffer, client_fd);
        if (dir == -1) {
            free(newpath);
            free(filedir);
            perror("[-] Could not recognize file :");
            return ERR;
        }

        memset(newpath, 0, 2048);
        memset(filedir, 0, 2048);

        if (dir == 1) {
            char *path = strtok(buffer + 4, " \n");
            snprintf(newpath, 2048, "%s/%s", STORAGE_DIR, path);
            int res = write_directory(client_fd, newpath);
            if (res == ERR) {
                perror("[-] Failed to download directory :");
                free(newpath);
                free(filedir);
                return ERR;
            }
        } else {
            char *path = strtok(buffer + 4, " \n");
            snprintf(newpath, 2048, "%s/%s", STORAGE_DIR, path);
            write_file(client_fd, newpath);
        }

        memset(buffer, 0, MAX_BUFFER_SIZE);
    }
    free(newpath);
    free(filedir);
    return 1;
}

/**
 * @brief Receive uploaded files or directories from the client.
 *
 * Determines if the client is sending a file or a directory and then
 * receives it accordingly using write_file or write_directory.
 *
 * @param client_fd The client's file descriptor.
 * @param path The path where the uploaded files/directories should be stored.
 * @return None
 */
void receive_upload(int client_fd, const char* path) {
    char buffer[MAX_BUFFER_SIZE];
    size_t bytes_read;
    int dir=-1;
    struct timeval timeout={5,0};
    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    int attempt=0;
    while (attempt<3 && dir==-1){
        bytes_read=recv(client_fd,buffer,MAX_BUFFER_SIZE,0);
        if (bytes_read==0){
            printf("Client connection closed");
            close(client_fd);
            break;
        }
        if (errno==EWOULDBLOCK || errno==EAGAIN){
            errno = 0;
            printf("[-] Timeout occurred, no data received\n");
            attempt++;
            continue;
        }
        dir=is_dir(buffer,client_fd);
        if (dir==-1) attempt++;
    }
    if (attempt==3){
        printf("[-] Could not receive new request\n");
        return;
    }

    client_session *client=get_client_session_by_socket(client_fd);
    if (client==NULL){
        printf("[-] Client session not found\n");
        close(client_fd);
        return;
    }
    char newpath[2048];
    snprintf(newpath, sizeof(newpath), "%s/%s", client->current_dir , path);
    printf("Receiving file at path: %s\n", newpath); 
    if (!dir){
        write_file(client_fd,newpath);
    }
    else {
        write_directory(client_fd,newpath);
    }
}

/**
 * @brief Sends a file from the server to the client.
 *
 * Reads the file from the given filename and sends it to the client in chunks.
 * It also handles retransmission attempts if necessary.
 *
 * @param client_fd The client's file descriptor.
 * @param filename The path to the file on the server to be sent.
 * @return None
 */
void send_file_to_client(int client_fd, const char* filename) {
    int attempt=0;
    struct timeval timeout={10,0};
    setsockopt(client_fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    while (attempt<3){
        FILE* file = fopen(filename, "rb");
        if (!file) {
            perror("Could not open file to read");
            send(client_fd, NACK, strlen(NACK), 0);
            return;
        }
        char buffer[MAX_BUFFER_SIZE];
        size_t bytes_read;

        printf("[+] Sending file: %s\n", filename);
        while ((bytes_read = fread(buffer, 1, MAX_BUFFER_SIZE, file)) > 0) {
            if (send(client_fd, buffer, bytes_read, 0) < 0) {
                perror("Error sending file");
                break;
            }
            printf("[+] Sent %zu bytes to client\n", bytes_read);
        }

        send(client_fd, END, LEN_END, 0);
        recv(client_fd,buffer,MAX_BUFFER_SIZE,0);
        if (errno==EWOULDBLOCK || errno==EAGAIN){
            errno = 0;
            printf("Timeout occurred, no data received\n");
            attempt++;
            fclose(file);
            continue;
        }
        if (strncmp(buffer,NACK,strlen(NACK))==0){
            printf("Client did not receive data correctly\n");
            attempt++;
            fclose(file);
            continue;
        }
        printf("[+] File '%s' sent successfully.\n", filename);
        fclose(file);
        return;
    }
}

/**
 * @brief Sends a directory and its contents (files and subdirectories) to the client.
 *
 * Iterates through the directory, sending information about files and subdirectories.
 * Uses send_file_to_client for files and send_directory recursively for directories.
 *
 * @param client_fd The client's file descriptor.
 * @param dir_path The path of the directory on the server to send.
 * @return None
 */
void send_directory(int client_fd, const char* dir_path) {
    DIR* dir = opendir(dir_path);
    if (!dir) {
        perror("Could not open directory");
        send(client_fd, NACK, strlen(NACK), 0);
        return;
    }

    struct dirent* entry;
    char new_path[1024];

    printf("[+] Sending directory: %s\n", dir_path);
    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) continue;

        snprintf(new_path, sizeof(new_path), "%s/%s", dir_path, entry->d_name);

        if (entry->d_type == DT_DIR) {
            char msg[1024];
            snprintf(msg, sizeof(msg), "dir %s", entry->d_name);
            send(client_fd, msg, strlen(msg), 0);
            char buffer[MAX_BUFFER_SIZE];
            recv(client_fd,buffer,MAX_BUFFER_SIZE,0);
            if (strncmp(buffer,ACK,strlen(ACK))==0){
                send_directory(client_fd,new_path);
            }
            else {
                printf("Directory %s cannot be upload\n",entry->d_name);
            }
        } else {
            char msg[1024];
            snprintf(msg, sizeof(msg), "file %s", entry->d_name);
            send(client_fd, msg, strlen(msg), 0);
            char buffer[MAX_BUFFER_SIZE];
            recv(client_fd,buffer,MAX_BUFFER_SIZE,0);
            if (strncmp(buffer,ACK,strlen(ACK))==0){
                send_file_to_client(client_fd,new_path);
            }
            else {
                printf("File %s cannot be upload\n",entry->d_name);
            }
        }
    }

    send(client_fd, END, LEN_END, 0);
    char resp[MAX_BUFFER_SIZE];
    recv(client_fd, resp,MAX_BUFFER_SIZE,0);
    if (strncmp(resp,ACK,strlen(ACK))==0){
        printf("[+] Directory '%s' sent successfully.\n", dir_path);
    }
    else {
        printf("[-] Directroy '%s' could not be uploaded",dir_path);
    }
    closedir(dir);
}

/**
 * @brief Handles incoming UDP broadcast messages and responds accordingly.
 *
 * If the message is a DISCOVER_SERVER request, the server responds with its address and port.
 * Also handles FILE_DISCOVER_SERVER requests by checking for file existence.
 *
 * @param fd The UDP socket file descriptor.
 * @param events The event flags.
 * @param arg A pointer to the Server structure.
 */
void on_udp_broadcast(evutil_socket_t fd, short events, void* arg) {
    Server* server = (Server*)arg;
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);

    int recv_len = recvfrom(fd, server->buff.buffer, MAX_BUFFER_SIZE, 0, (struct sockaddr*)&client_addr, &addr_len);
    if (recv_len < 0) {
        perror("[-] Error receiving UDP message");
        return;
    }

    server->buff.buffer[recv_len] = '\0';
    printf("Received broadcast message: %s\n", server->buff.buffer);
    if (strncmp(server->buff.buffer,"DISCOVER_SERVER",16)==0){
        char response[1024];
        snprintf(response, sizeof(response), "%s:%d", inet_ntoa(server->serv_addr.sin_addr), ntohs(server->serv_addr.sin_port));
        if (sendto(fd, response, strlen(response), 0, (struct sockaddr*)&client_addr, addr_len) < 0) {
            perror("[-] Error sending UDP response");
        } else {
            printf("Sent discovery response: %s\n", response);
        }
    }
    else if (strncmp(server->buff.buffer,"FILE_DISCOVER_SERVER",20)==0){
        char* filename = strtok(server->buff.buffer + 21, " \n");
        int bytes=look_for_file(filename,STORAGE_DIR);
        if (bytes>0){
            char response[1024];
            snprintf(response, sizeof(response), "%s:%d", inet_ntoa(server->serv_addr.sin_addr), ntohs(server->serv_addr.sin_port));
            if (sendto(fd, response, strlen(response), 0, (struct sockaddr*)&client_addr, addr_len) < 0) {
                perror("[-] Error sending UDP response");
            } else {
                printf("Sent discovery response: %s\n", response);
            }
        }
    }
}

/**
 * @brief Starts the event loop for the server.
 *
 * Registers the TCP and UDP event callbacks and then dispatches the event loop,
 * which will process client connections, incoming data, and UDP broadcasts.
 *
 * @param server A pointer to the Server structure.
 * @return None
 */
void start_event_loop(Server* server) {
    server->base = event_base_new();
    event_add(event_new(server->base, server->tcp_fd, EV_READ | EV_PERSIST, on_accept, server), NULL);
    event_add(event_new(server->base, server->udp_fd, EV_READ | EV_PERSIST, on_udp_broadcast, server), NULL);
    printf("[+] Starting event loop...\n");
    event_base_dispatch(server->base);
}

/**
 * @brief Changes the current working directory of the client's session.
 *
 * Validates the requested directory to ensure it doesn't escape the server's storage directory.
 * Updates the client's current directory on success.
 *
 * @param client_fd The client's file descriptor.
 * @param newDir The requested new directory path (relative or absolute).
 * @return None
 */
void change_directory(int client_fd, const char *newDir) {
    char buffer[PATH_MAX];
    char absPath[PATH_MAX];
    static char normalizedStorageDir[PATH_MAX] = {0};
    client_session *currSession = get_client_session_by_socket(client_fd);

    printf("[DEBUG] Client requested change to directory: '%s'\n", newDir);
    printf("[DEBUG] Current directory: '%s'\n", currSession->current_dir);

    if (normalizedStorageDir[0]== '\0') {
        if (realpath(STORAGE_DIR, normalizedStorageDir) == NULL) {
            err("Couldn't retrieve STORAGE_DIR", 1);
        }
        size_t len = strlen(normalizedStorageDir);
        if (len > 1 && normalizedStorageDir[len - 1] == '/') {
            normalizedStorageDir[len - 1] = '\0'; 
        }
        printf("[INFO] Storage root resolved to: %s\n", normalizedStorageDir);
    }

    if (newDir[0] == '/') {
        strncpy(buffer, newDir, PATH_MAX);
        printf("[DEBUG] Absolute path provided: '%s'\n", buffer);
    } else {
        snprintf(buffer, PATH_MAX, "%s/%s", currSession->current_dir, newDir);
        printf("[DEBUG] Constructed relative path: '%s'\n", buffer);
    }

    if (realpath(buffer, absPath) == NULL) {
        perror("[-] realpath failed");
        SEND_ERROR(client_fd, DIRECTORY_ERROR);
        return;
    }

    printf("[DEBUG] Canonical absolute path resolved: '%s'\n", absPath);

    if (strncmp(absPath, normalizedStorageDir, strlen(normalizedStorageDir)) != 0) {
        printf("[-] Out of bounds! Resolved path: '%s', Storage root: '%s'\n", absPath, normalizedStorageDir);
        SEND_ERROR(client_fd, "[-] Out of bounds!");
        return;
    }

    if (!directory_exists(absPath)) {
        printf("[-] Directory does not exist: '%s'\n", absPath);
        SEND_ERROR(client_fd, DIRECTORY_ERROR);
        return;
    }

    strncpy(currSession->current_dir, absPath, PATH_MAX);
    printf("[DEBUG] Updated current directory to: '%s'\n", currSession->current_dir);


    send(client_fd, ACK, strlen(ACK), 0);
    printf("[DEBUG] ACK sent to client.\n");
}

/**
 * @brief Prints the current working directory of the client's session.
 *
 * Sends the client's current working directory path back to the client.
 *
 * @param client_fd The client's file descriptor.
 * @return None
 */
void print_working_dir(int client_fd) {
    client_session* sess = get_client_session_by_socket(client_fd);
    if (sess == NULL) {
        send(client_fd, "no_session", strlen("no_session"),0);
        err("[-] Error retrieving session",-1);
    }
    printf("Sending sess->current_dir : %s \n", sess->current_dir);
    send(client_fd, sess->current_dir, strlen(sess->current_dir),0);
}

/**
 * @brief Callback function triggered when data is available from the client.
 *
 * Parses and processes commands sent by the client such as upload, download, cd, and pwd.
 *
 * @param fd The client's file descriptor.
 * @param events The event flags.
 * @param arg A pointer to the Server structure.
 * @return None
 */
void on_client_data(evutil_socket_t fd, short events, void* arg) {
    Server* server = (Server*)arg;
    int res = read(fd, server->buff.buffer, MAX_BUFFER_SIZE);
    if (res <= 0) {
        printf("Client disconnected\n");
        close(fd);
        return;
    }

    server->buff.buffer[res] = '\0';
    if (strncmp(server->buff.buffer, "upload", strlen("upload")) == 0) {
        char* path = strtok(server->buff.buffer + strlen("upload") + 1, " \n");
        if (path) {
            send(fd,ACK,strlen(ACK),0);
            receive_upload(fd, path);
        } else {
            send(fd,NACK,strlen(NACK),0);
            printf("[-] No path provided for upload\n");
        }
    } else if (strncmp(server->buff.buffer, "download", strlen("download")) == 0) {
        char* path = strtok(server->buff.buffer + strlen("download")+1, " \n");
        if (path) {
            client_session* client=get_client_session_by_socket(fd);
            char fullpath[1024];
            snprintf(fullpath, sizeof(fullpath), "%s/%s", client->current_dir, path);

            int dir = check_download_request(fullpath);

            if (dir == 0) {
                send(fd, "file", strlen("file"), 0);
                send_file_to_client(fd, fullpath);
            } else if (dir == 1) {
                send(fd, "dir", strlen("dir"), 0);
                send_directory(fd, fullpath);
            } else {
                send(fd, NACK, strlen(NACK), 0);
                printf("Invalid path for download: %s\n", path);
            }
        } else {
            printf("No path provided for download\n");
            send(fd, NACK, strlen(NACK), 0);
        }
    } else if (strncmp(server->buff.buffer, "cd", strlen("cd")) == 0) {
        char* path = strtok(server->buff.buffer + strlen("cd") + 1, " \n");
        if (path) {
            change_directory(fd, path);
        } else {
            printf("[-] No path provided for cd\n");
        }
    } else if (strncmp(server->buff.buffer, "pwd", strlen("pwd")) == 0) {
            print_working_dir(fd);
             
    } else if (strncmp(server->buff.buffer, "list", strlen("list")) == 0) {
        client_session* sess = get_client_session_by_socket(fd);
        if (sess) {
            DIR* dir = opendir(sess->current_dir);
            if (!dir) {
                perror("[-] Could not open current directory");
                send(fd, "NACK", strlen("NACK"), 0);
                return;
            }
            struct dirent* entry;
            char buffer[MAX_BUFFER_SIZE] = {0};
            while ((entry = readdir(dir)) != NULL) {
                if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0)
                    continue; // Ignore les répertoires spéciaux
                snprintf(buffer, sizeof(buffer), "%s\n", entry->d_name);
                send(fd, buffer, strlen(buffer), 0);
            }
            closedir(dir);
            send(fd, "END", strlen("END"), 0); // Signal de fin
            char boufeur [MAX_BUFFER_SIZE];
            recv(fd, boufeur, MAX_BUFFER_SIZE, 0);
            }
    }
}

/**
 * @brief The main entry point of the program.
 *
 * Initializes the server with given arguments and starts the event loop.
 *
 * @param argc The argument count.
 * @param argv The argument vector. Expected usage: ./program <port> <interface>
 * @return int Returns 1337 on success, and may exit earlier on errors.
 */
int main(int argc, char** argv) {
    if (argc != 3) printf("[-] Usage : %s <port> <interface>", argv[0]), exit(2);

    int port;
    if ((port = atoi(argv[1])) == 0) err(Port have to be a number or different from 0, 3);
    printf("Initializing server...\n");
    Server server;
    init(&server, port,argv[2]);
    printf("[+] Server initialized !\n");
    start_event_loop(&server);
    return 1337;
}
