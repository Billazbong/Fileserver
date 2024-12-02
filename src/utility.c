#include "../include/utility.h"

int check_end_signal(char *buffer,int len){
    if (len<LEN_END){
        return 0;
    }
    return strncmp(buffer+len-LEN_END,END,LEN_END)==0;
}