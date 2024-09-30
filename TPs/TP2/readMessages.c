#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include "includes/readMessages.h"
#include <unistd.h>
#include <sys/types.h>
#include <time.h>
#include <sys/wait.h>

const char* get_username() {
    const char *username = getenv("USER");
    if (username == NULL) {
        perror("Erro ao obter o nome de usuário");
        exit(EXIT_FAILURE);
    }
    return username;
}

const char* getRemetente(const char *filepath) {
    FILE *file = fopen(filepath, "r");
    if (file == NULL) {
        printf("Erro ao abrir o arquivo: %s\n", filepath);
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    if (ftell(file) == 0) {
        printf("O arquivo está vazio: %s\n", filepath);
        fclose(file);
        return NULL;
    }
    rewind(file);

    char *line = NULL;
    size_t len = 0;
    ssize_t read;
    read = getline(&line, &len, file);
    if (read == -1) {
        printf("Erro ao ler a linha do arquivo: %s\n", filepath);
        fclose(file);
        return NULL;
    }
    fclose(file);
    return line;
}

char *getConteudo(const char *filepath) {
  FILE *fp = fopen(filepath, "r");
  if (fp == NULL) {
    return NULL;
  }

  fseek(fp, 0, SEEK_END);
  long fsize = ftell(fp);
  fseek(fp, 0, SEEK_SET);

  char *content = malloc(fsize + 1);
  if (content == NULL) {
    fclose(fp);
    return NULL;
  }

  fread(content, 1, fsize, fp);
  content[fsize] = '\0';

  fclose(fp);
  return content;
}

int readMessage(const char *inbox, const char *archive, int mid) {
  DIR *dir;
  dir = opendir(inbox);
  if (dir == NULL) {
    printf("Erro ao abrir a pasta: %s\n", inbox);
    return 1;
  }

  struct dirent *entrada;
  int found = 0;
  while ((entrada = readdir(dir)) != NULL) {
    if (atoi(entrada->d_name) == mid) {
        char filepath[512];
        snprintf(filepath, sizeof(filepath), "%s/%s", inbox, entrada->d_name);
        char *content = getConteudo(filepath);
        if (content != NULL) {
          printf("%s\n", content);
          free(content);
          pid_t pid = fork();
          if (pid == 0) {
              execlp("mv", "mv", filepath, archive, (char *) NULL);
              exit(EXIT_FAILURE);
          } else if (pid < 0) {
              printf("Error forking a new process.\n");
          } else {
              int status;
              waitpid(pid, &status, 0);
          }
          found = 1;
          break;
        }
    }
  }

  if (!found) {
    printf("File '%d' not found in the Inbox directory.\n", mid);
  }

  closedir(dir);
  return found ? 0 : 1;
}

void listMessages(const char *inbox) {
  DIR *dir;
  dir = opendir(inbox);
  if (dir == NULL) {
    printf("Erro ao abrir a pasta: %s\n", inbox);
    return;
  }

  struct dirent *entrada;
  while ((entrada = readdir(dir)) != NULL) {
    if (strcmp(entrada->d_name, ".") != 0 && strcmp(entrada->d_name, "..") != 0) {
      char filepath[512];
      snprintf(filepath, sizeof(filepath), "%s/%s", inbox, entrada->d_name);

      struct stat file_stat;
      if (stat(filepath, &file_stat) == -1) {
        printf("Erro ao obter informações sobre o arquivo: %s\n", filepath);
        continue;
      }
      printf("%s: %ld bytes\n", entrada->d_name, file_stat.st_size);
    }
  }

  closedir(dir);
}

void listMessagesA(const char *inbox) {
    DIR *dir;
    dir = opendir(inbox);
    if (dir == NULL) {
        printf("Erro ao abrir a pasta: %s\n", inbox);
        return;
    }   
    struct dirent *entrada;
    while ((entrada = readdir(dir)) != NULL) {
        if (strcmp(entrada->d_name, ".") != 0 && strcmp(entrada->d_name, "..") != 0) {
            char filepath[512];
            snprintf(filepath, sizeof(filepath), "%s/%s", inbox, entrada->d_name);  
            struct stat file_stat;
            if (stat(filepath, &file_stat) == -1) {
                printf("Erro ao obter informações sobre o arquivo: %s\n", filepath);
                continue;
            }
            const char *line = getRemetente(filepath);
            printf("[%s]\n", entrada->d_name);
            printf("Data de receção: %s", ctime(&file_stat.st_mtime));
            printf("Remetente: %s", line);
            printf("Tamanho da mensagem: %ld bytes\n", file_stat.st_size);
        }
    }   
    closedir(dir);
}

void removeMessage(const char *archive, int mid) {
    DIR *dir;
    dir = opendir(archive);
    if (dir == NULL) {
        printf("Erro ao abrir a pasta: %s\n", archive);
        return;
    }

    struct dirent *entrada;
    int found = 0;
    while ((entrada = readdir(dir)) != NULL) {
        if (atoi(entrada->d_name) == mid) {
            char filepath[512];
            snprintf(filepath, sizeof(filepath), "%s/%s", archive, entrada->d_name);
            pid_t pid = fork();
            if (pid == 0) {
                execlp("rm", "rm", filepath, (char *) NULL);
                exit(EXIT_FAILURE);
            } else if (pid < 0) {
                printf("Error forking a new process.\n");
            } else {
                int status;
                waitpid(pid, &status, 0);
            }
            found = 1;
            break;
        }
    }

    if (!found) {
        printf("File '%d' not found in the archive directory.\n", mid);
    }

    closedir(dir);
}

void removeAllMessages(const char *archive) {
    DIR *dir;
    dir = opendir(archive);
    if (dir == NULL) {
        printf("Erro ao abrir a pasta: %s\n", archive);
        return;
    }

    struct dirent *entrada;
    while ((entrada = readdir(dir)) != NULL) {
        if (strcmp(entrada->d_name, ".") != 0 && strcmp(entrada->d_name, "..") != 0) {
            char filepath[512];
            snprintf(filepath, sizeof(filepath), "%s/%s", archive, entrada->d_name);
            if (remove(filepath) == -1) {
                printf("Erro ao remover o arquivo: %s\n", filepath);
            }
        }
    }

    closedir(dir);
}