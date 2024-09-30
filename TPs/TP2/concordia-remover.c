#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <dirent.h>
#include <stdbool.h>
#include <time.h>
#include "includes/readMessages.h"

#define MAX_MESSAGE_LEN 512
#define MAX_BUFFER_SIZE 256

// Definição da estrutura de mensagem
#include "includes/mensagem.h"

#define FIFO_SERVER "/tmp/concordia"

int main(int argc, char *argv[]) {
    if (argc < 2 || argc > 3) {
        printf("Usage: %s <remover mid | tudo> \n", argv[0]);
        exit(EXIT_FAILURE);
    }
    const char *username = get_username();
    const char *homedir = getenv("HOME");

    char archive[256];
    snprintf(archive, sizeof(archive), "%s/concordia-%s/archive", homedir, username);
    DIR *dir;
    dir = opendir(archive);
    if (dir == NULL) {
      printf("Erro ao abrir a pasta: %s\n", archive);
      exit(1);
    }

    if (strcmp(argv[1], "remover") == 0 && (argc == 3)) {
        removeMessage(archive, atoi(argv[2]));
    } else if ((strcmp(argv[1], "tudo") == 0) && argc == 2) {
        removeAllMessages(archive);
    }
    closedir(dir);
    return 0;
}