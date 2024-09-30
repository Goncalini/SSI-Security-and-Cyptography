#include <syslog.h>

int main(int agrc, char *argv[]){
    int i = 0;
    while(1){
        syslog(LOG_INFO,"%s: %d", "My Daemon", i++);
        sleep(1);
    }
    return 0;
}