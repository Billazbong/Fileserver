#pragma once

#include <errno.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>

#include "ip_helper.h"
#include "buffer.h"

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define err(s,n) {perror("[-] In file "__FILE__" at line "TOSTRING(__LINE__)": "#s);exit(n);}

#define ERR -1
#define MAX_CLIENT 10
#define STORAGE_DIR "/var/lib/myfileserver/"
#define INTERFACE "enp0s3" //normalement c eth0

/**
 * @brief Represents a server instance and its associated data.
 */
typedef struct {
    int server_fd;                            // File descriptor for the server socket.
    int epoll_fd;                             // File descriptor for the epoll instance
    int nfds;                                 // Used to store the number of events triggered by epoll_wait()
    struct epoll_event ev;                    // Epoll event to bind the sockets to the epoll instance
    struct epoll_event events[MAX_CLIENT];    // Array to hold events from epoll_wait()
    struct sockaddr_in serv_addr;             // Server's address information (IP address and port).
    Buffer buff;
} Server;