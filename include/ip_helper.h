#pragma once

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <ifaddrs.h>
#include <sys/types.h>
#include <sys/socket.h>
#include "constants.h"

extern char host[TOKEN_SIZE];
in_addr_t get_local_ip_of_interface(const char* interface_name);