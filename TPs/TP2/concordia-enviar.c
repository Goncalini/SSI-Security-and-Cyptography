#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
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

//./concordia-enviar dest msg
int main(int args, char* argv[]){
    if(args < 3){
        printf("Usage: %s <dest> <msg>\n", argv[0]);
        return 1;
    }
    //vai ver se a mensagem tem o tamanho certo
    char *mensg = argv[2];
    int tamanho = strlen(mensg);
    if(tamanho <= 0){
        printf("Mensagem necessária!\n");
        return 1;
    }else if(tamanho > 512){
        printf("Mensagem é maior do que permitida (máx. 512 caracteres)!\n");
        return 1;
    }


    int client_fd = open(FIFO_SERVER, O_WRONLY);
    if (client_fd == -1) {
        perror("Falha ao abrir FIFO do cliente");
        exit(EXIT_FAILURE);
    }

    //username do remetente
    const char *username = getenv("USER");
    if (username == NULL) {
        perror("Erro ao obter o nome de usuário");
        return 1;
    }else{
        printf("Username: %s\n", username);
    }

    Message msg;
    strcpy(msg.command, "concordia-enviar");
    strcpy(msg.argument1, username);
    strcpy(msg.argument2, argv[1]); //username do destino
    sprintf(msg.argument3, "%d", tamanho); //tamanho da mensagem
    strcpy(msg.argument4, mensg); //mensagem

    // Escrever a mensagem no FIFO do servidor
    ssize_t bytes_written = write(client_fd, &msg, sizeof(msg));
    if (bytes_written == -1) {
        perror("Erro ao escrever na FIFO do cliente");
        close(client_fd);
        exit(EXIT_FAILURE);
    }

    close(client_fd);
    
    return 0;
}