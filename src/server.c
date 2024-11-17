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
    if (stat(STORAGE_DIR, &st)!=ERR) {
        printf("[!] Storage directory already exists at : %s\n",STORAGE_DIR);
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
void init(Server* server, int port) {

    
    printf("Setting up the storage directory...\n");
    setup_storage_dir();
    init_with_capacity(&server->buff,MAX_LEN);

    printf("Setting up the socket...\n");
    server->tcp_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->tcp_fd < 0) err(Could not initialize the server socket, 4);

    printf("Setting up the epoll instance...\n");
    server->epoll_fd=epoll_create1(0);
    if (server->epoll_fd == -1) err(Failed to create epoll instance, 6);
    server->ev.events=EPOLLIN;
    server->ev.data.fd=server->tcp_fd;
    if (epoll_ctl(server->epoll_fd,EPOLL_CTL_ADD,server->tcp_fd,&server->ev)) err(Could not add the socket to the epoll instance,9);

    printf("Setting up server address...\n");
    server->serv_addr.sin_family=AF_INET;
    if ((server->serv_addr.sin_addr.s_addr=get_local_ip_of_interface(INTERFACE))==ERR) err(Could not get local ip of the interface,12);

    server->serv_addr.sin_port=htons(port);

    printf("Binding the socket and the address...\n");
    int res;
    res=bind(server->tcp_fd, (struct sockaddr*) &server->serv_addr, sizeof(server->serv_addr));
    if (res==ERR) err(Could not bind the socket to the local address,7);

    res=listen(server->tcp_fd,MAX_CLIENT);
    if (res==ERR) err(Could not set the socket to listen,8);
    printf("Listening...\n");

        // Setup UDP socket for discovery
    server->udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (server->udp_fd < 0) err("Could not create UDP socket", 13);

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

    if (bind(server->udp_fd, (struct sockaddr*) &udp_addr, sizeof(udp_addr)) < 0) {
        perror("Could not bind UDP socket");
        exit(1);
    }

    printf("UDP socket bound for broadcast discovery on port %d\n", BROADCAST_PORT);
}

/**
 * @brief Handles UDP broadcast discovery requests.
 * 
 * This function listens for incoming broadcast messages (DISCOVER_SERVER).
 * When received, it responds with the server's IP address and port.
 */
void handle_broadcast_discovery(Server* server) {
    printf("coucou\n");
    char buffer[MAX_LEN];
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);

    // Receive UDP broadcast message
    int recv_len = recvfrom(server->udp_fd, buffer, sizeof(buffer), 0, (struct sockaddr*)&client_addr, &addr_len);
    if (recv_len < 0) {
        perror("Error receiving UDP message");
        return;
    }

    buffer[recv_len] = '\0';  // Null-terminate the received message
    printf("Received broadcast message: %s\n", buffer);

    // Respond to the discovery request with the server's address
    char response[MAX_LEN];
    snprintf(response, sizeof(response), "%s:%d", inet_ntoa(server->serv_addr.sin_addr), ntohs(server->serv_addr.sin_port));

    if (sendto(server->udp_fd, response, strlen(response), 0, (struct sockaddr*)&client_addr, addr_len) < 0) {
        perror("Error sending UDP response");
    } else {
        printf("Sent discovery response: %s\n", response);
    }
}

int event_loop(Server* server){
    for(;;){
        server->nfds = epoll_wait(server->epoll_fd, server->events, MAX_CLIENT, -1);
        if (server->nfds == ERR) err(Could not retrieve any events,10);
        handle_broadcast_discovery(server);
         for (int i=0;i<server->nfds;i++){
            if (server->events[i].data.fd==server->tcp_fd){  //* Case when new client to add
                int client_fd = accept(server->tcp_fd,0,0);
                if (client_fd == ERR) err(Could not accept the client,11);
                server->ev.events=EPOLLIN;
                server->ev.data.fd=client_fd;
                if (epoll_ctl(server->epoll_fd,EPOLL_CTL_ADD,client_fd,&server->ev)==ERR) {
                    perror("[-] Could not bind the client socket to the epoll instance");
                    close(client_fd);
                }
                printf("[!] New client connected\n");
            }
            else { // Handle the data
                int res=read(server->events[i].data.fd,server->buff.buffer,MAX_LEN);
                if(res==ERR) {
                    close(server->events[i].data.fd);
                    epoll_ctl(server->epoll_fd,EPOLL_CTL_DEL,server->events[i].data.fd,NULL);
                }
                else {
                    write(server->events[i].data.fd, server->buff.buffer, res);
                }
            }
         }
    }
}


int main(int argc, char** argv ){
    if (argc != 2) printf("[-] Usage : %s <port>",argv[0]), exit(2);

    int port;
    if ((port = atoi(argv[1])) == 0) err(Port have to be a number or different from 0, 3);
    printf("Initializing server...\n");
    Server server;
    init(&server, port);
    printf("[+] Server initialized !\n");
    event_loop(&server);
    return 1337;
}
