#ifndef MESSAGE_H
#define MESSAGE_H

#define MAX_MESSAGES 100
#define MAX_GROUPS 10
#define MAX_MEMBERS 10

typedef struct {
    char command[32];
    char argument1[100];
    char argument2[100];
    char argument3[100];
    char argument4[464];
} Message;

#endif