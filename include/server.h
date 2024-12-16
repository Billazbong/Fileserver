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
/**
 * @brief Macro for error reporting and exiting.
 *
 * Prints an error message (including file and line number) and exits the program with the given code.
 *
 * @param s The error message.
 * @param n The exit code.
 */
#define err(s, n) { perror("[-] In file "__FILE__" at line "TOSTRING(__LINE__)": " #s); exit(n); }

/**
 * @brief Represents a single client session.
 *
 * A client session stores the client's socket descriptor and the current working directory for that client.
 */
typedef struct {
    int socket;             /**< The client's socket descriptor. */
    char current_dir[2048]; /**< The client's current working directory. */
} client_session;

/**
 * @brief Represents a server instance and its associated data.
 *
 * This structure holds the server's TCP and UDP socket file descriptors,
 * its address structure, a buffer for handling data, an event base for libevent,
 * and an array of client sessions.
 */
typedef struct {
    int tcp_fd;                      /**< File descriptor for the TCP socket. */
    int udp_fd;                      /**< File descriptor for the UDP socket. */
    struct sockaddr_in serv_addr;    /**< Server's address information (IP address and port). */
    Buffer buff;                     /**< Buffer for handling client data. */
    struct event_base* base;         /**< Event base for libevent handling asynchronous events. */
    client_session clients[MAX_CLIENT]; /**< Array of client sessions. */
} Server;

/**
 * @brief Signal indicating the end of transmission.
 */
#define END_SIGNAL "END"
/**
 * @brief Length of the END_SIGNAL string.
 */
#define LEN_END 3
/**
 * @brief Negative acknowledgment (NACK) signal for failed reception.
 */
#define NACK "NACK"
/**
 * @brief Acknowledgment (ACK) signal for successful reception.
 */
#define ACK "ACK"

// Function prototypes

/**
 * @brief Sets up the storage directory.
 *
 * Checks if the storage directory exists. If it doesn't, creates it with
 * permissions set to 0700. Otherwise, prints a message indicating its existence.
 */
void setup_storage_dir();

/**
 * @brief Initializes the server.
 *
 * Sets up the server's storage directory, creates the TCP and UDP sockets,
 * binds them to the specified port and interface, and prepares the server structure.
 *
 * @param server A pointer to the Server structure to be initialized.
 * @param port The port number the server will listen on.
 * @param interface The network interface name the server binds to.
 */
void init(Server* server, int port, const char * interface);

/**
 * @brief Starts the server's event loop.
 *
 * Registers the necessary events and dispatches the event loop that will
 * handle client connections, incoming data, and UDP broadcasts.
 *
 * @param server A pointer to the Server structure.
 */
void start_event_loop(Server* server);

/**
 * @brief Callback function triggered upon a new client connection.
 *
 * Handles accepting a new client and sets up the event for reading data
 * from that client.
 *
 * @param fd The listening socket file descriptor.
 * @param events Event flags.
 * @param arg A pointer to the Server structure.
 */
void on_accept(evutil_socket_t fd, short events, void* arg);

/**
 * @brief Callback function triggered when data is available from a client.
 *
 * Reads incoming data from the client, processes commands (upload, download, cd, pwd),
 * and performs the requested actions.
 *
 * @param fd The client's file descriptor.
 * @param events Event flags.
 * @param arg A pointer to the Server structure.
 */
void on_client_data(evutil_socket_t fd, short events, void* arg);

/**
 * @brief Callback function triggered when a UDP broadcast is received.
 *
 * Handles DISCOVER_SERVER and FILE_DISCOVER_SERVER messages. Responds with
 * the server's address and port if conditions are met.
 *
 * @param fd The UDP socket file descriptor.
 * @param events Event flags.
 * @param arg A pointer to the Server structure.
 */
void on_udp_broadcast(evutil_socket_t fd, short events, void* arg);
