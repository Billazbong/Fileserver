#pragma once

#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define err(s,n) {perror("In file "__FILE__" at line "TOSTRING(__LINE__)": "#s);exit(n);}

#define ERR -1
#define STORAGE_DIR "/var/lib/myfileserver/"
#define MAX_CLIENT 10


/**
 * @brief Represents a server instance and its associated data.
 */
typedef struct 
{
    int server_fd;                            ///< File descriptor for the server socket.
    struct epoll_event ev;
    struct epoll_event events[MAX_CLIENT];    ///< Array to hold events from epoll_wait()
    int epoll_fd;                             ///< File descriptor for the epoll instance
    struct sockaddr_in serv_addr;             ///< Server's address information (IP address and port).
} Server;