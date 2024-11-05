#include <errno.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <errno.h>

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define err(s,n) {perror("In file "__FILE__" at line "TOSTRING(__LINE__)": "#s);exit(n);}

#define STORAGE_DIR "/var/lib/myfileserver/"
#define MAX_CLIENT 10

typedef struct 
{
    int server_fd; // Server socket
    int client_fds[MAX_CLIENT]; // Array of the client sockets
    fd_set client_fdset; // File descriptor set for select()
    int max_fd; // Max file descriptor for select()
    struct sockaddr_in serv_addr;
}Server;

/*Function to setup the storage directory if it does not exists*/

void setup_stordir(){
    struct stat st={0};
    if (stat(STORAGE_DIR,&st)==-1) {
        if (mkdir(STORAGE_DIR,0700)==-1) err(Could not setup the storage directory,5)
        else printf("Storage directory created at : %s\n", STORAGE_DIR);
    }
    else printf("Storage directory already exists at : %s\n",STORAGE_DIR);
}


/*Function to initialize the server*/

void init(Server *server,int port){
    
    printf("Setting up the storage directory...\n");
    setup_stordir();

    memset(server,0,sizeof(Server));
    server->server_fd=socket(AF_INET, SOCK_STREAM, 0);

    if (server->server_fd<0) err(Could not initialize the server socket,4);
    server->max_fd=server->server_fd;
}


int main(int argc, char **argv){
    if (argc !=2) err(Wrong number of argument,2);
    int port;
    if ((port=atoi(argv[1]))==0) err(Port have to be a number or different from 0,3);
    Server server;
    printf("Initializing server...\n");
    init(&server,port);
    return 43;
}