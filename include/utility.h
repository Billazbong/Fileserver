#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "constants.h"
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <event2/event.h>
#include <dirent.h>
#include <stdbool.h>

int check_end_signal(char *buffer,int len);
int is_dir(char *buffer,int client_fd);
int get_file_size(char *filename);
int look_for_file(char *filename,char *path);
int directory_exists(const char* directory);