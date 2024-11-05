#pragma once

#include <sys/socket.h>
#include <sys/select.h>
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
    int server_fd;                 ///< File descriptor for the server socket.
    int client_fds[MAX_CLIENT];    ///< Array to store file descriptors of connected clients.
    fd_set client_fdset;           ///< File descriptor set used for `select()` to monitor client activity.
    int max_fd;                    ///< Highest file descriptor value being monitored (used with `select()`).
    struct sockaddr_in serv_addr;  ///< Server's address information (IP address and port).
} Server;