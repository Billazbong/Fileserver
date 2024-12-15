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
#include <netinet/in.h>
#include <arpa/inet.h>
#include <event2/event.h>
#include <limits.h>

#include "ip_helper.h"
#include "buffer.h"
#include "utility.h"
#include "constants.h"

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)
#define err(s, n) { perror("[-] In file "__FILE__" at line "TOSTRING(__LINE__)": " #s); exit(n); }

typedef struct {
    int socket;
    char current_dir[1024];
} client_session;

/**
    * @brief Represents a server instance and its associated data.
 */
typedef struct {
    int tcp_fd;                      // File descriptor for the TCP socket.
    int udp_fd;                      // File descriptor for the UDP socket.
    struct sockaddr_in serv_addr;    // Server's address information (IP address and port).
    Buffer buff;                     // Buffer for handling client data.
    struct event_base* base;         // Event base for libevent.
    client_session clients[MAX_CLIENT];
} Server;

#define END_SIGNAL "END"      // Signal pour indiquer la fin de la transmission
#define LEN_END 3             // Longueur du signal "END"
#define NACK "NACK"           // Signal d'erreur pour la non-réception
#define ACK "ACK"             // Signal de confirmation de réception

// Function prototypes
void setup_storage_dir();
void init(Server* server, int port, const char * interface);
void start_event_loop(Server* server);
void on_accept(evutil_socket_t fd, short events, void* arg);
void on_client_data(evutil_socket_t fd, short events, void* arg);
void on_udp_broadcast(evutil_socket_t fd, short events, void* arg);