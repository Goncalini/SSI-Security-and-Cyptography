#ifndef MAILQUEUE_H
#define MAILQUEUE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_MESSAGES 100
#define MAX_MEMBERS 10


typedef struct mail{
    int mid; 
    char to[16];
    char from[16];
    int size;
    char text[513];
}Mail;

typedef struct queue{
    Mail messages[MAX_MESSAGES];
    int front;
    int size;
}Queue;

void initQueue(Queue *q);
int isEmptyQueue(Queue *q);
int enqueue(Queue *q, Mail m);
int dequeue(Queue *q, Mail *m);

#endif