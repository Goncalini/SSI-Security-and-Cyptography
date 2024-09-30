#ifndef READMESSAGES_H
#define READMESSAGES_H

const char *get_username(void);
const char *getRemetente(const char *filepath);
char *getConteudo(const char *filepath);

int readMessage(const char *inbox, const char* archive, int mid);
void listMessages(const char *inbox);
void listMessagesA(const char *inbox);
void removeMessage(const char *archive, int mid);
void removeAllMessages(const char *archive);

#endif