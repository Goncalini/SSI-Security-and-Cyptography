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
        printf("Usage: %s <mid | listar> [-a]\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    const char *username = get_username();
    const char *homedir = getenv("HOME");

    char inbox[256];
    snprintf(inbox, sizeof(inbox), "%s/concordia-%s/inbox", homedir, username);
    char archive[256];
    snprintf(archive, sizeof(archive), "%s/concordia-%s/archive", homedir, username);
    DIR *dir;
    dir = opendir(inbox);
    if (dir == NULL) {
      printf("Erro ao abrir a pasta: %s\n", inbox);
      exit(1);
    }

    if (strcmp(argv[1], "ler") == 0 && (argc == 3)) {
        return readMessage(inbox, archive, atoi(argv[2]));
    } else if ((strcmp(argv[1], "listar") == 0) && argc == 2) {
        listMessages(inbox);
    } else if ((strcmp(argv[1], "listar") == 0) && (strcmp(argv[2], "-a") == 0) && (argc == 3)) {
        listMessagesA(inbox);
    }
    closedir(dir);
    return 0;
}