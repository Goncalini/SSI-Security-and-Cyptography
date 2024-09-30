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

#define MAX_MESSAGE_LEN 512
#define MAX_BUFFER_SIZE 256

// Definição da estrutura de mensagem
#include "includes/mensagem.h"

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

    const char *homedir = getenv("HOME");
    if (homedir != NULL) {
        char pathi[256];
        char patha[256];
        char path[256];
        snprintf(pathi, sizeof(pathi), "%s/concordia-%s/inbox", homedir, pw->pw_name);
        snprintf(patha, sizeof(patha), "%s/concordia-%s/archive", homedir, pw->pw_name);
        snprintf(path, sizeof(path), "%s/concordia-%s", homedir, pw->pw_name);
        
        pid_t pid = fork();
        if (pid == 0) {
            execlp("rm", "rm", "-r", pathi, NULL);
            perror("Falha ao remover diretoria inbox");
            exit(EXIT_FAILURE);
        } else if (pid > 0) {
            wait(NULL);

            pid = fork();
            if (pid == 0) {
                execlp("rm", "rm", "-r", patha, NULL);
                perror("Falha ao remover diretoria archive");
                exit(EXIT_FAILURE);
            } else if (pid > 0) {
                wait(NULL);

                pid = fork();
                if (pid == 0) {
                    execlp("rm", "rm", "-r", path, NULL);
                    perror("Falha ao remover diretoria");
                    exit(EXIT_FAILURE);
                } else if (pid > 0) {
                    wait(NULL);
                } else {
                    perror("Falha ao criar processo filho");
                    exit(EXIT_FAILURE);
                }           
            }else {
                perror("Falha ao criar processo filho");
                exit(EXIT_FAILURE);
            }
        } else {
            perror("Falha ao criar processo filho");
            exit(EXIT_FAILURE);
        }
    }

    pid_t pid = fork();
    if (pid == 0) {
        execlp("usermod", "usermod", "-G", "", pw->pw_name,  NULL);
        perror("execl");
    } else if (pid < 0) {
        perror("fork");
    } else {
        wait(NULL);
    }

    int client_fd = open(FIFO_SERVER, O_WRONLY);
    if (client_fd == -1) {
        perror("Falha ao abrir FIFO do cliente");
        exit(EXIT_FAILURE);
    }

    Message msg;
    strcpy(msg.command, "concordia-desativar");
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
