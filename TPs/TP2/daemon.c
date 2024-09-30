#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>
#include <time.h>
#include <dirent.h>
#include <stdbool.h>

#include "includes/mensagem.h"
#include "includes/hashusers.h"
#include "includes/mailqueue.h"
#include "grupos.c"

#define FIFO_SERVER "/tmp/concordia"

//Variáveis globais
bool hashInitialized = false; //!A retirar
int message_counter = 0;

Queue msgqueue;


//----------Handlers----------

//concordia-ativar
void handleActivationRequest(const char* name, HashUser h){
    printf("New user: %s\n", name);
    addMemberToGroup(name, h);
    printHashUser(h);
}

//concordia-desativar
void handleDeactivationRequest(const char* name, HashUser hu){
    printf("User deactivated: %s\n", name);
    NodoUser user = lookupUser(name, hu);
    if(user == NULL){
        printf("Utilizador não existe no Concordia!");
    }
    //remocao do nodo da hash
    int posicao = hash(name);
    NodoUser *item;
    for (item = hu + posicao; (*item) != NULL && (strcmp((*item)->user.username, name) != 0); item = &((*item)->next))
        ; //enquanto a hash não for vazia e a key não for igual, avança na hash
    if(*item != NULL){
        NodoUser temp = *item;
        *item = (*item)->next;
        free(temp);
    }
}

//concordia-enviar
void handleSendRequest(const char*to, const char*from, const char*size, char* message, HashUser hu){
    NodoUser destination = lookupUser(to, hu);
    if(destination == NULL){
        char members[MAX_MEMBERS][50];
        int numMembers = getMembers(to, members);

        if (numMembers == 0){
            printf("Utilizador %s não existe no Concordia!", to);
            return;
        }
    }

    Mail msg;
    msg.mid = message_counter++;
    strncpy(msg.to, to, sizeof(msg.to));
    strncpy(msg.from, from, sizeof(msg.from));
    msg.size = atoi(size);
    strncpy(msg.text, message, sizeof(msg.text));
    if (enqueue(&msgqueue,msg)){
        printf("Queue is full!\n");
    } else {
        printf("Message added to queue!\n");
    }
}

//concordia-grupo-adicionar-membro
void handleAddUserToGroup(const char* username, const char* groupname,const char*memberadd, HashUser hu) {
    NodoUser user = lookupUser(username, hu);
    if(user == NULL){
        printf("Utilizador %s não existe no Concordia!", username);
        return;
    }
    if(!addMemberToGroupG(groupname,username,memberadd)){
        printf("Não foi possível adicionar utilizador ao grupo");
        return;
    }
}


//concordia-grupo-criar
void handleCreateGroup(const char* username, const char* groupname, HashUser hu){
    NodoUser user = lookupUser(username, hu);
    if(user == NULL){
        printf("Utilizador %s não existe no Concordia!", username);
        return;
    }
    createGroup(groupname,username);
}


//concordia-grupo-remover
void handleRemoveGroup(const char* username, const char* groupname, HashUser hu){
    NodoUser user = lookupUser(username, hu);
    if(user == NULL){
        printf("Utilizador %s não existe no Concordia!", username);
    }
    if(removeGroupFromFile(groupname, username)){
        printf("Grupo Removido!");
    }
}


//concordia-grupo-remover-membro
void handleRemoveUserFromGroup(const char* username, const char* groupname, const char* memberToRemove, HashUser hu){
    NodoUser user = lookupUser(username, hu);
    if(user == NULL){
        printf("Utilizador %s não existe no Concordia!", username);
    }
    if(!removeMemberFromGroup(groupname,username,memberToRemove)) printf("Grupo Removido!");
}

//concordia-grupo-listar
void handleListGroup(const char* groupName, HashUser hu){
    char members[MAX_MEMBERS][50];
    int numMembers = getMembers(groupName, members);

    if (numMembers > 0) {
        printf("Membros do grupo:\n");
        for (int i = 0; i < numMembers; i++) {
            printf("%s\n", members[i]);
        }
    }else{
        printf("Grupo %s não existe!\n",groupName);
    }
}




//----------Acessos à queue global----------

//Retira mensagens da queue e coloca-as na inbox do utilizador
void sendMessage(Mail msg){
    //aceder ao endereço da pasta do utilizador destino
    char *to_username = msg.to;
    char inbox[100];
    snprintf(inbox, sizeof(inbox), "/home/%s/concordia-%s/inbox", to_username, to_username);
    printf("Inbox destiny: %s\n", inbox);
    DIR *dir;
    dir = opendir(inbox);
    if (dir == NULL) {
        printf("Erro ao abrir a pasta: %s\n", inbox);
        return;
    }

    //Cria um novo ficheiro .txt para a mensagem
    char filename[256];
    snprintf(filename, sizeof(filename), "%s/%d.txt", inbox, msg.mid); 
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        printf("Erro ao criar o arquivo: %s\n", filename);
        closedir(dir);
        return;
    }
    //coloca lá a mensagem no formato => remetente\n tamanho\n mensagem
    fprintf(file, "%s\n%d\n", msg.from, msg.size);
    fprintf(file, "%s", msg.text);

    fclose(file);

    chmod(filename,420);
    closedir(dir);
}


//Envia as mensagens aos utilizadores apartir da queue
void processMessageQueue(){
    Mail newMsg;

    if(dequeue(&msgqueue, &newMsg)){
        printf("Queue is empty!\n");
    } else {
        sendMessage(newMsg);
    }
}


//----------Main----------

void childProcess(int server_fd, HashUser h) {
    Message msg;
    ssize_t bytes_read;
    while ((bytes_read = read(server_fd, &msg, sizeof(msg))) > 0) {

        char command[32];
        sscanf(msg.command, "%s", command);
        char argument1[100];
        sscanf(msg.argument1, "%s", argument1);
        char argument2[100];
        sscanf(msg.argument2, "%s", argument2);
        char argument3[100];
        sscanf(msg.argument3, "%s", argument3);
        char argument4[100];
        sscanf(msg.argument4, "%s", argument4);

        // Verifica o comando
        if (strcmp(command, "concordia-ativar") == 0) {
            handleActivationRequest(argument1, h);
        } else if (strcmp(command, "concordia-desativar") == 0) {
            handleDeactivationRequest(argument1, h);
        } else if (strcmp(command, "concordia-enviar") == 0 || strcmp(command, "concordia-responder") == 0){
            handleSendRequest(argument2, argument1, argument3, argument4, h);
        } else if (strcmp(command, "concordia-grupo-criar") == 0){
            handleCreateGroup(argument1, argument2, h);
        }else if(strcmp(command, "concordia-grupo-adicionar-membro") == 0){
             handleAddUserToGroup(argument1, argument2,argument3,h);
        }else if (strcmp(command, "concordia-grupo-listar") == 0) {
            handleListGroup(argument2, h);
        } else if (strcmp(command, "concordia-grupo-remover") == 0){
            handleRemoveGroup(argument1, argument2, h);
        }else if(strcmp(command, "concordia-grupo-remover-membro") == 0) {
            void handleRemoveUserFromGroup(argument1, argument2, argument3, h);
        }else {
            printf("Comando desconhecido: %s\n", command);
        }  
    }
    if (bytes_read == -1) {
        perror("Erro ao ler da FIFO");
    }

    //close(server_fd);
    //exit(EXIT_SUCCESS);
}



int main() {
    printf("%d\n",1);
    HashUser h;
    initHashUsers(h);
    hashInitialized = true;
    initQueue(&msgqueue);
    

    int server_fd = open(FIFO_SERVER, O_RDONLY);
    if (server_fd == -1) {
        perror("Falha ao abrir FIFO");
        exit(EXIT_FAILURE);
    }
    while (1) {
        if(!isEmptyQueue(&msgqueue)){
            processMessageQueue(); 
        }
        childProcess(server_fd, h);
    }

    close(server_fd);
    //Remover FIFO
    unlink(FIFO_SERVER);

    //Libertar memória da Hashtable
    freeHashUser(h);

    return 0;
}



//!User=daemon
