CC = gcc
CFLAGS = -Wall -Wextra
BIN_DIR = bin
INCLUDE_DIR = includes

CONCORDIA_ATIVAR_SRC := concordia-ativar.c mensagem.c
CONCORDIA_LER_SRC := concordia-ler.c readMessages.c
CONCORDIA_ENVIAR_SRC := concordia-enviar.c
DAEMON_SRC := daemon.c mailqueue.c hashusers.c

CONCORDIA_ATIVAR_OBJ := $(BIN_DIR)/concordia-ativar.o
CONCORDIA_LER_OBJ := $(patsubst %.c,$(BIN_DIR)/%.o,$(CONCORDIA_LER_SRC))
CONCORDIA_ENVIAR_OBJ := $(patsubst %.c,$(BIN_DIR)/%.o,$(CONCORDIA_ENVIAR_SRC))
DAEMON_OBJ := $(patsubst %.c,$(BIN_DIR)/%.o,$(DAEMON_SRC))

all: directories concordia-ativar concordia-ler concordia-enviar daemon

directories: 
	mkdir -p $(BIN_DIR)

concordia-ativar: $(CONCORDIA_ATIVAR_OBJ)
	$(CC) $(CFLAGS) $^ -o $(BIN_DIR)/$@

concordia-ler: $(CONCORDIA_LER_OBJ)
	$(CC) $(CFLAGS) $^ -o $(BIN_DIR)/$@

concordia-enviar:  $(CONCORDIA_ENVIAR_OBJ) $(INCLUDE_DIR)/mensagem.h
	$(CC) $(CFLAGS) $^ -o $(BIN_DIR)/$@

daemon: $(DAEMON_OBJ) $(INCLUDE_DIR)/mensagem.h $(INCLUDE_DIR)/hashusers.h $(INCLUDE_DIR)/mailqueue.h
	$(CC) $(CFLAGS) $^ -o $(BIN_DIR)/$@

$(BIN_DIR)/%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(BIN_DIR)