#include "../include/ip_helper.h"    

in_addr_t get_local_ip_of_interface(const char* interface_name) {
    struct ifaddrs *ifaddr, *ifa;
    in_addr_t ip_addr = INADDR_NONE;
    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return INADDR_NONE;
    }

    for (ifa = ifaddr; ifa; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr 
            && ifa->ifa_addr->sa_family == AF_INET 
            && strcmp(ifa->ifa_name, interface_name) == 0) {
            struct sockaddr_in* ipv4 = (struct sockaddr_in*)ifa->ifa_addr;
            ip_addr = ipv4->sin_addr.s_addr;
            break;
        }
    }
    
    freeifaddrs(ifaddr);
    return ip_addr;
}
