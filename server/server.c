#include <errno.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <fcntl.h>
#include <netinet/in.h>

#define MAX_CLIENT 10

typedef struct 
{
    int server_sock; // Server socket
    int client_socks[MAX_CLIENT]; // Array of the client sockets
    fd_set client_fds; // File descriptor set for select()
    int max_fd; // Max file descriptor for select()
    struct sockaddr_in serv_addr;
}Server;


void init(Server server){
    
}


int main(int argc, char **argv){
    Server server;
    init(server);
}