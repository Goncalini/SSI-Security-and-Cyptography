#include "includes/mailqueue.h"

void initQueue(Queue *q){
    q->front = 0;
    q->size = 0;
}

int isEmptyQueue(Queue *q){
    return(q->size == 0);
}

int enqueue(Queue *q, Mail m){
    int r = 0;
    if(q->size == MAX_MESSAGES) r = 1;
    else{
        q->messages[(q->front + q->size++) % MAX_MESSAGES] = m;
    }
    return r;
}

int dequeue(Queue *q, Mail *m){
    int r = 0;
    if(q->size == 0) r = 1;
    else{
        *m = q->messages[q->front];
        q->front = (q->front + 1)%MAX_MESSAGES;
        q->size--;
    }
    return r;
}
