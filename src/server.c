#include "../include/server.h"

/**
    * @brief Sets up the storage directory.
    * Checks if the storage directory exists. 
    * If it doesn't exist, creates the directory with permissions set to 0700.
    * If the directory already exists, prints a message indicating its existence.
    *
    * @param None
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
   * creates a socket for the server, and initializes the 
   * server structure.
   *
   * @param server A pointer to the Server structure to be initialized.
   * @param port The port number the server will listen on. 
*/
void init(Server* server, int port, const char* interface) {
    printf("Setting up the storage directory...\n");
    setup_storage_dir();
    init_with_capacity(&server->buff, MAX_LEN);

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

    struct event* client_event = event_new(server->base, client_fd, EV_READ | EV_PERSIST, on_client_data, server);
    event_add(client_event, NULL);
}

void on_client_data(evutil_socket_t fd, short events, void* arg) {
    Server* server = (Server*)arg;
    int res = read(fd, server->buff.buffer, MAX_LEN);
    if (res <= 0) {
        printf("Client disconnected\n");
        close(fd);
        return;
    }
    write(fd, server->buff.buffer, res);
}

void on_udp_broadcast(evutil_socket_t fd, short events, void* arg) {
    Server* server = (Server*)arg;
    char buffer[MAX_LEN];
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);

    int recv_len = recvfrom(fd, buffer, sizeof(buffer), 0, (struct sockaddr*)&client_addr, &addr_len);
    if (recv_len < 0) {
        perror("Error receiving UDP message");
        return;
    }

    buffer[recv_len] = '\0';
    printf("Received broadcast message: %s\n", buffer);

    char response[1024];
    snprintf(response, sizeof(response), "%s:%d", inet_ntoa(server->serv_addr.sin_addr), ntohs(server->serv_addr.sin_port));

    if (sendto(fd, response, strlen(response), 0, (struct sockaddr*)&client_addr, addr_len) < 0) {
        perror("Error sending UDP response");
    } else {
        printf("Sent discovery response: %s\n", response);
    }
}

void start_event_loop(Server* server) {
    server->base = event_base_new();
    event_add(event_new(server->base, server->tcp_fd, EV_READ | EV_PERSIST, on_accept, server), NULL);
    event_add(event_new(server->base, server->udp_fd, EV_READ | EV_PERSIST, on_udp_broadcast, server), NULL);
    printf("[+] Starting event loop...\n");
    event_base_dispatch(server->base);
}

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
