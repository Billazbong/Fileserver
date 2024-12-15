#pragma once

#include "constants.h"
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <event2/event.h>
#include <dirent.h>
#include <stdbool.h>

/**
 * @brief Checks if the end of transmission signal (END) is present at the end of the buffer.
 *
 * @param buffer The data buffer.
 * @param len The length of the buffer.
 * @return `int`: 1 if the end signal is found, 0 otherwise.
 */
int check_end_signal(char *buffer,int len);

/**
 * @brief Determines if the received buffer indicates a directory or a file.
 *
 * Sends an ACK or NACK back to the client based on the recognized command.
 *
 * @param buffer The data buffer containing either "dir" or "file".
 * @param client_fd The client's file descriptor.
 * @return `int`: 1 if directory, 0 if file, -1 if unrecognized.
 */
int is_dir(char *buffer,int client_fd);

/**
 * @brief Retrieves the file size of a given file.
 *
 * @param filename The name of the file.
 * @return `int`: The size of the file in bytes, or -1 if the file doesn't exist.
 */
int get_file_size(char *filename);

/**
 * @brief Searches for a file in a directory (and its subdirectories).
 *
 * @param filename The target filename to look for.
 * @param path The path of the directory to search.
 * @return `int`: The size of the file if found, 0 if not found, or -1 on error.
 */
int look_for_file(char *filename,char *path);

/**
 * @brief Checks if a path refers to a regular file or directory for download requests.
 *
 * @param path The path to check.
 * @return `int`: 0 if file, 1 if directory, -1 if invalid.
 */
int check_download_request(char* path);

/**
 * @brief Checks if a given directory exists.
 *
 * @param directory The path of the directory to check.
 * @return `int`: Non-zero if the directory exists, 0 otherwise.
 */
int directory_exists(const char* directory);
