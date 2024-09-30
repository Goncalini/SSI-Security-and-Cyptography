#ifndef HASHUSERS_H
#define HASHUSERS_H

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_MESSAGES 100
#define MAX_MEMBERS 10
#define MAX_GROUPS 10

typedef struct user{
    char username[50];
    int num_messages;
    char groups[MAX_GROUPS][100];
    int num_groups;
} User;

typedef struct nodoUser{
    User user;
    struct nodoUser *next;
} *NodoUser;

typedef NodoUser HashUser[MAX_MEMBERS];

size_t hash(const char *str);
void initHashUsers(HashUser h);
void addMemberToGroup(const char *name, HashUser h);
NodoUser lookupUser(const char *key, HashUser hu);
void freeHashUser(HashUser hu);
void printUser(NodoUser u);
void printHashUser(HashUser table);

#endif