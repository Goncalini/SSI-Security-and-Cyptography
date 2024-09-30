#ifndef GRUPOS_H
#define GRUPOS_H

#define MAX_MEMBERS 10

typedef struct grupo{
    char name[50]; //nome do grupo
    char creator[50]; //nome do criador
    char members[MAX_MEMBERS][50]; //nomes dos membros
    int num_members;
} Grupo;

void createGroup(const char* groupName, const char* creator);
int removeGroupFromFile(const char* groupName, const char* username);
int getMembers(const char* groupName, char members[MAX_MEMBERS][50]);
int addMemberToGroupG(const char* groupName, const char* username, const char* newMember);
int removeMemberFromGroup(const char* groupName, const char* username, const char* memberToRemove);


#endif