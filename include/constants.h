#pragma once

#define ERR -1
#define MAX_CLIENT 10
#define MAX_LEN 1024
#define STORAGE_DIR "/Users/nity/fileServer/"
#define BROADCAST_PORT 9999

#define TOKEN_SIZE 1024
#define ACK "ACK"
#define END "END"
#define NACK "NACK"
#define LEN_END 3

#define MAX_BUFFER_SIZE 8192

#define SEND_ERROR(client_fd, message) send(client_fd, message, strlen(message), 0)
#define DIRECTORY_ERROR "[-] Directory doesn't exist or can't be accessed"