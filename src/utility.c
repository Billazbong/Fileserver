#include "../include/utility.h"

int check_end_signal(char *buffer,int len){
    if (len<LEN_END){
        return 0;
    }
    return strncmp(buffer+len-LEN_END, END, LEN_END)==0;
}

int is_dir(char *buffer,int client_fd){
    int is_dir;
    if (strncmp(buffer,"dir",3)==0){
        send(client_fd, ACK, strlen(ACK), 0);
        is_dir=1;
        printf("Directory received\n");
    }
    else if (strncmp(buffer,"file",4)==0){
        send(client_fd, ACK, strlen(ACK), 0);
        is_dir=0;
        printf("File received\n");
    }
    else {
        send(client_fd, NACK, strlen(NACK), 0);
        is_dir=-1;
        printf("Could not recognize request");
    }
    return is_dir;
}

int check_download_request(char* path){
    struct stat st;
    if (stat(path, &st) == -1) {
        perror("Could not find path");
        return -1;
    }
    if (S_ISDIR(st.st_mode)){
        return 1;
    }
    else if (S_ISREG(st.st_mode)){
        return 0;
    }
    return -1;
}

int get_file_size(char *filename){
    struct stat st;
    if (stat(filename, &st) == -1) {
        perror("Could not get file size");
        return -1;
    }
    return st.st_size;
}

int directory_exists(const char* directory) {
    struct stat dirStat;
    return (!(stat(directory, &dirStat) != 0 || !S_ISDIR(dirStat.st_mode)));
}

int look_for_file(char *filename,char *path){
    struct dirent *entry;
    struct stat st;
    DIR *dp = opendir(path);

    if (dp == NULL) {
        perror("opendir");
        return -1;
    }

    while ((entry=readdir(dp))){
        char fullpath[1024];
        snprintf(fullpath, sizeof(fullpath), "%s/%s", path, entry->d_name);
        if (stat(fullpath, &st) == 0) {
            if (S_ISDIR(st.st_mode)) {
                if (strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0) {
                    int res=0;
                    if ((res=look_for_file(filename, fullpath))>0) {
                        closedir(dp);
                        return res;
                    }
                }
            } else if (S_ISREG(st.st_mode)) {
                if (strcmp(entry->d_name, filename) == 0) {
                    closedir(dp);
                    return get_file_size(fullpath);
                }
            }
        }
    }
    closedir(dp);
    return 0;
}
