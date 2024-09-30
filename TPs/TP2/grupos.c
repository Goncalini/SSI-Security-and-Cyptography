#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "includes/grupos.h"


// Criar um novo grupo
void createGroup(const char* groupName, const char* creator) {
    char filename[256];
    snprintf(filename, sizeof(filename), "groups/%s.txt", groupName); 
    FILE *file = fopen(filename, "w");
    if (file == NULL) {
        perror("Erro ao abrir o arquivo de grupos");
        exit(EXIT_FAILURE);
    }
    fprintf(file, "%s\n%d\n%s\n", creator, 1, creator);
    fclose(file);
}



int removeGroupFromFile(const char* groupName, const char* username) {
    char filename[256];
    char c[50];

    snprintf(filename, sizeof(filename), "groups/%s.txt", groupName); 
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Erro ao abrir o arquivo de grupos");
        exit(EXIT_FAILURE);
    }

    fscanf(file, "%[^\n]", c);
    fclose(file);

    if (strcmp(username, c) != 0) {
        printf("Apenas o criador do grupo pode removê-lo.\n");
        return 0;
    }

    if (remove(filename) != 0) {
        perror("Erro ao remover o arquivo de grupos");
        exit(EXIT_FAILURE);
    }
    return 1;
}


int getMembers(const char* groupName, char members[MAX_MEMBERS][50]) {
    char filename[256];
    snprintf(filename, sizeof(filename), "groups/%s.txt", groupName); 
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Erro ao abrir o arquivo de grupos");
        exit(EXIT_FAILURE);
    }

    int numMembers = 0;
    char creator[50];

    fscanf(file, "%[^\n]\n", creator);
    fscanf(file, "%d\n", &numMembers);

    for (int i = 0; i < numMembers; i++) {
        fscanf(file, "%[^\n]\n", members[i]);
    }

    fclose(file);

    if (numMembers == 0) {
        printf("Grupo %s não encontrado ou sem membros.\n", groupName);
        return 0;
    }

    return numMembers;
}


int addMemberToGroupG(const char* groupName, const char* username, const char* newMember){
    char filename[256];
    snprintf(filename, sizeof(filename), "groups/%s.txt", groupName); 
    FILE *file = fopen(filename, "r+");
    if (file == NULL) {
        perror("Erro: grupo não encontrado");
        exit(EXIT_FAILURE);
    }
    char line[100];

    int numMembers;
    int i;
    Grupo g;

    fscanf(file, "%[^\n]\n", g.creator);
    if(strcmp(username,g.creator)!= 0){
        printf("Apenas o usuário que criou o grupo pode adicionar membros.\n");
        fclose(file);
        return 0;
    }

    fscanf(file, "%d\n",g.num_members);
    for (int i = 0; i < g.num_members; i++) {
        fscanf(file, "%[^\n]\n", g.members[i]);
    }
    strcpy(g.members[g.num_members], newMember);
    g.num_members++;
    rewind(file);

    // Escreve as informações atualizadas no arquivo
    fprintf(file, "%s\n%d\n", g.creator, g.num_members);
    for(int i = 0; i < g.num_members; i++){
        fprintf(file, "%s\n", g.members[i]);
    }

    fclose(file);
    return 1;
}


int removeMemberFromGroup(const char* groupName, const char* username, const char* memberToRemove) {
    char filename[256];
    snprintf(filename, sizeof(filename), "groups/%s.txt", groupName); 
    FILE *file = fopen(filename, "r+");
    if (file == NULL) {
        perror("Erro ao abrir o arquivo de grupos");
        exit(EXIT_FAILURE);
    }
    
    Grupo g;
    char line[50];

    fscanf(file, "%[^\n]\n", g.creator);
    if(strcmp(username,g.creator)!= 0){
        printf("Apenas o usuário que criou o grupo pode adicionar membros.\n");
        fclose(file);
        return 0;
    }
    fscanf(file, "%d\n",&g.num_members);
    for (int i = 0; i < g.num_members; i++) {
        fscanf(file, "%[^\n]\n", line);
        if(strcmp(line, memberToRemove) == 0){
            g.num_members--;
        }else{
            strcpy(g.members[i], line);
        }
       
    }

    rewind(file);
    // Escreve as informações atualizadas no arquivo
    fprintf(file, "%s\n%d\n", g.creator, g.num_members);
    for(int i = 0; i < g.num_members; i++){
        fprintf(file, "%s\n", g.members[i]);
    }

    fclose(file);

    return 1;

}