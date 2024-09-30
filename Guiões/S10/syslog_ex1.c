 #include <syslog.h>
//envia as mensagens para o servidor - priority = severidade
//void syslog(int priority, const char *format, ...);


int main(){

    //void openlog(const char *ident, int option, int facility); -> facility é uma forma de filtrar
    openlog("programa_S10",LOG_PID | LOG_PERROR,LOG_USER);

    //define o nivel minimo de severidade
    setlogmask(LOG_UPTO(LOG_INFO)); //melhor usar o LOG_UPTO do que o LOG_MASK

    //void syslog(int priority, const char *format, ...); - format é o formato de texto de c

    syslog (LOG_DEBUG, "%s","OLA"); //com o setlogmask a log_info, este já não aparece

    syslog(LOG_ALERT,"%s","PERIGO!");

    closelog();
    
    return 0;
}
