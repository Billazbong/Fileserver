#pragma once

#include "storage_directory.h"

#define ERR -1
#define MAX_CLIENT 10
#define MAX_LEN 1024
#define BROADCAST_PORT 9999
#define TOKEN_SIZE 1024

/**
 * @brief Acknowledgment message sent to clients after successful operations.
 */
#define ACK "ACK"

/**
 * @brief End-of-transmission signal sent to indicate no more data is coming.
 */
#define END "END"

/**
 * @brief Negative acknowledgment signal sent to indicate an error in receiving data.
 */
#define NACK "NACK"

/**
 * @brief Length of the END signal.
 */
#define LEN_END 3

/**
 * @brief Maximum size of the transfer buffer.
 */
#define MAX_BUFFER_SIZE 8192

/**
 * @brief Macro to send an error message to the client.
 */
#define SEND_ERROR(client_fd, message) send(client_fd, message, strlen(message), 0)

/**
 * @brief Error message sent when a directory doesn't exist or can't be accessed.
 */
#define DIRECTORY_ERROR "[-] Directory doesn't exist or can't be accessed"
