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

    init_with_capacity(&server->buff,MAX_LEN);
    
    printf("Setting up the storage directory...\n");
    setup_storage_dir();

    memset(server, 0, sizeof(Server));

    printf("Setting up the socket...\n");
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd < 0) err(Could not initialize the server socket, 4);

    printf("Setting up the epoll instance...\n");
    server->epoll_fd=epoll_create1(0);
    if (server->epoll_fd == -1) err(Failed to create epoll instance, 6);
    server->ev.events=EPOLLIN;
    server->ev.data.fd=server->server_fd;
    if (epoll_ctl(server->epoll_fd,EPOLL_CTL_ADD,server->server_fd,&server->ev)) err(Could not add the socket to the epoll instance,9);

    printf("Setting up server address...\n");
    server->serv_addr.sin_family=AF_INET;
    server->serv_addr.sin_addr.s_addr=get_local_ip_of_interface(INTERFACE);
    server->serv_addr.sin_port=htons(port);

    printf("Binding the socket and the address...\n");
    int res;
    res=bind(server->server_fd, (struct sockaddr*) &server->serv_addr, sizeof(server->serv_addr));
    if (res==ERR) err(Could not bind the socket to the local address,7);

    res=listen(server->server_fd,MAX_CLIENT);
    if (res==ERR) err(Could not set the socket to listen,8);
    printf("Listening...\n");
}

int event_loop(Server* server){
    for(;;){
        server->nfds = epoll_wait(server->epoll_fd, server->events, MAX_CLIENT, -1);
        if (server->nfds == ERR) err(Could not retrieve any events,10);

         for (int i=0;i<server->nfds;i++){
            if (server->events[i].data.fd==server->server_fd){  //* Case when new client to add
                int client_fd = accept(server->server_fd,0,0);
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
