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
    if (stat(STORAGE_DIR, &st)) {
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
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (server->server_fd < 0) err(Could not initialize the server socket, 4);
        server->max_fd = server->server_fd;
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