#include <errno.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

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
        printf("Storage directory already exists at : %s\n",STORAGE_DIR);
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

    memset(server, 0, sizeof(Server));


    printf("Setting up the socket...\n");
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd < 0) err(Could not initialize the server socket, 4);
    printf("Server socket successfully created \n");

    printf("Setting up the epoll instance...\n");
    server->epoll_fd=epoll_create1(0);
    if (server->epoll_fd == -1) err(Failed to create epoll instance, 6);
    printf("Epoll instance successfully created\n");

    printf("Adding server socket to epoll instance...\n");
    server->ev.events=EPOLLIN;
    server->ev.data.fd=server->server_fd;
    if (epoll_ctl(server->epoll_fd,EPOLL_CTL_ADD,server->server_fd,&server->ev)) err(Could not add the socket to the epoll instance,9);
    printf("Server socket successfully added to epoll instance\n");

    printf("Setting up server address...\n");
    server->serv_addr.sin_family=AF_INET;
    server->serv_addr.sin_addr.s_addr=INADDR_ANY;
    server->serv_addr.sin_port=htons(port);
    printf("Server address successfully set up\n");


    printf("Binding the socket and the address...\n");
    int res;
    res=bind(server->server_fd, (struct sockaddr_in *) &server->serv_addr, sizeof(server->serv_addr));
    if (res==ERR) err(Could not bind the socket to the local address,7);
    printf("Binding successful\n");

    printf("Starting to listen...\n");
    res=listen(server->server_fd,MAX_CLIENT);
    if (res==ERR) err(Could not set the socket to listen,8);
    printf("Listening...\n");
}


int main(int argc, char** argv ){
    if (argc != 2) err(Wrong number of argument, 2); //todo : Montrer l'utilisation correcte du programme ( Usage : argv[0] <argument> .. )
    int port;
    if ((port = atoi(argv[1])) == 0) err(Port have to be a number or different from 0, 3);

    printf("Initializing server...\n");
    Server server;
    init(&server, port);

    return 1337;
}
