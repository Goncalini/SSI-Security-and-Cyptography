#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
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

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <grupo>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    uid_t uid = getuid(); 
    struct passwd *pw = getpwuid(uid);
    if (pw != NULL) {
        printf("Username: %s\n", pw->pw_name);
    }

    int client_fd = open(FIFO_SERVER, O_WRONLY);
    if (client_fd == -1) {
        perror("Falha ao abrir FIFO do cliente");
        exit(EXIT_FAILURE);
    }

    Message msg;
    const char* groupname = argv[1];
    strcpy(msg.command, "concordia-grupo-criar");
    strcpy(msg.argument1, pw->pw_name);
    strcpy(msg.argument2, groupname);

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
