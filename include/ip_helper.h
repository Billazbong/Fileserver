#pragma once

#include <netinet/in.h>
#include <ifaddrs.h>
#include <string.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>

/**
 * @brief Retrieves the IP address of a specified network interface.
 *
 * @param interface_name The name of the network interface (e.g., "eth0").
 *
 * @return `in_addr_t`: The IP address of the specified interface, or `INADDR_NONE` if 
 * the interface is not found or has no associated IP address.
 *
 * @code
 * in_addr_t ip = get_local_ip_of_interface("eth0");
 * @endcode
 */
in_addr_t get_local_ip_of_interface(const char* interface_name);
