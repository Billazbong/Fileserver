#include "../include/utility.h"

int check_end_signal(char *buffer,int len){
    if (len<LEN_END){
        return 0;
    }
    return strncmp(buffer+len-LEN_END,END,LEN_END)==0;
}

int is_dir(char *buffer,int client_fd){
    int is_dir;
    if (strncmp(buffer,"dir",3)==0){
        is_dir=1;
        printf("Directory received\n");
        send(client_fd,ACK,strlen(ACK),0);
    }
    else if (strncmp(buffer,"file",4)==0){
        is_dir=0;
        printf("File received\n");
        send(client_fd,ACK,strlen(ACK),0);
    }
    else {
        is_dir=-1;
        printf("Could not recognize request");
        send(client_fd,NACK,strlen(NACK),0);
    }
    return is_dir;
}