#include "includes/hashusers.h"

size_t hash(const char *str){
    unsigned long hash = MAX_MEMBERS;
    int c;
    while ((c = *str++))
    {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % MAX_MEMBERS;
}


void initHashUsers(HashUser h){
    for(long i = 0; i < MAX_MEMBERS; i++){
        h[i] = NULL;
    }
}

// Aux
void addMemberToGroup(const char *name, HashUser h) {
    int posicao = hash(name);
    //inicializa utilizador
    NodoUser member = malloc(sizeof(struct nodoUser));
    if (member == NULL) {
        fprintf(stderr, "Erro: Falha ao alocar memória.\n");
        exit(EXIT_FAILURE);
    }
    strcpy(member->user.username, name);
    member->user.num_messages = 0;
    member->user.num_groups = 0;

    member->next = h[posicao];
    h[posicao] = member;
}


NodoUser lookupUser(const char *key, HashUser hu){
    int posicao = hash(key);
    NodoUser current = hu[posicao];
    while (current != NULL && strcmp(current->user.username, key) != 0){
        current = current->next;
    }
    printf("User found: %s\n", current->user.username);
    return current;
}


void freeHashUser(HashUser hu){
    if(hu!=NULL){
        for(int i = 0; i < MAX_MEMBERS; i++){
            NodoUser current = hu[i];
            while (current != NULL) {
                NodoUser temp = current;
                current = current->next;
                free(temp);
            }
        }
    }
}


void printUser(NodoUser u)
{
    printf("%s | %d | %d\n", u->user.username, u->user.num_messages,  u->user.num_groups);
    if (u->next == NULL)
    {
        printf("    Next empty.\n");
    }
}

void printHashUser(HashUser table)
{
    //proint e calcula n elem
    int n = 0;
    for (int i = 0; i < MAX_MEMBERS; i++)
    {
        NodoUser current = table[i];
        while (current != NULL)
        {
            printUser(current);
            current = current->next;
            n++;
        }
    }
}
