#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <pwd.h>
#include <grp.h>

// Definição da estrutura de mensagem
#include "includes/mensagem.h"

#define MAX_MESSAGE_LEN 512
#define MAX_BUFFER_SIZE 256

#define FIFO_SERVER "/tmp/concordia"

const char* get_username() {
    const char *username = getenv("USER");
    if (username == NULL) {
        perror("Erro ao obter o nome de usuário");
        exit(EXIT_FAILURE);
    }
    return username;
}

int main() {
    uid_t uid = getuid(); 
    struct passwd *pw = getpwuid(uid);
    if (pw != NULL) {
        printf("Username: %s\n", pw->pw_name);
    }

    pid_t pid = fork();
    if (pid == 0) {
        execlp("usermod", "usermod", "-aG", "concordia", pw->pw_name, NULL);
        perror("execl");
    } else if (pid < 0) {
        perror("fork");
    } else {
        wait(NULL);
    }
    const char *homedir = getenv("HOME");
    if (homedir != NULL) {
        char path[256];
        char pathi[256];
        char patha[256];
        snprintf(path, sizeof(path), "%s/concordia-%s", homedir, pw->pw_name);
        snprintf(pathi, sizeof(pathi), "%s/concordia-%s/inbox", homedir, pw->pw_name);
        snprintf(patha, sizeof(patha), "%s/concordia-%s/archive", homedir, pw->pw_name);
        mkdir(path, 0772);
        mkdir(pathi, 0772);
        mkdir(patha, 0772);
        pid_t pid;

        char acl[256];
        snprintf(acl, sizeof(acl), "u:%s:rwx", pw->pw_name);

        // For path
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl, path, (char *) NULL);
            exit(EXIT_FAILURE);
        }

        // For pathi
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl, pathi, (char *) NULL);
            exit(EXIT_FAILURE);
        }

        // For patha
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl, patha, (char *) NULL);
            exit(EXIT_FAILURE);
        }



        char acl2[256];
        snprintf(acl2, sizeof(acl), "u:core:rwx", pw->pw_name);

        // For path
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl2, path, (char ) NULL);
            exit(EXIT_FAILURE);
        }

        // For pathi
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl2, pathi, (char) NULL);
            exit(EXIT_FAILURE);
        }

        // For patha
        pid = fork();
        if (pid == 0) {
            execl("/usr/bin/setfacl", "setfacl", "-m", acl2, patha, (char *) NULL);
            exit(EXIT_FAILURE);
        }
    }

    int client_fd = open(FIFO_SERVER, O_WRONLY);
    if (client_fd == -1) {
        perror("Falha ao abrir FIFO do cliente");
        exit(EXIT_FAILURE);
    }

    Message msg;
    strcpy(msg.command, "concordia-ativar");
    strcpy(msg.argument1, pw->pw_name);

    //Escrever a mensagem no FIFO do servidor
    ssize_t bytes_written = write(client_fd, &msg, sizeof(msg));
    if (bytes_written == -1) {
        perror("Erro ao escrever na FIFO do cliente");
        close(client_fd);
        exit(EXIT_FAILURE);
    }

    close(client_fd);

    return 0;
}
