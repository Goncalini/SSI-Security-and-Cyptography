#!/bin/bash

# Diretório de arquivos C
C_DIR="src"

# Opções de compilação do GCC (opcional)
GCC_FLAGS=""

# Diretório de saída para executáveis
OUT_DIR="/usr/bin"

# Função para verificar se o usuário é root
is_root() {
  if [ "$(whoami)" = "root" ]; then
    true
  else
    echo "Este script deve ser executado como root."
    exit 1
  fi
}

# Função para compilar um arquivo C
compile_file() {
    c_file_base=$1
    if [ "$c_file_base" = "concordia-ler" ]; then
      gcc "$c_file_base.c" readMessages.c -o "$OUT_DIR/$c_file_base"
    elif [ "$c_file_base" = "concordia-remover" ]; then
      gcc "$c_file_base.c" readMessages.c -o "$OUT_DIR/$c_file_base"
    elif [ "$c_file_base" = "concordia-responder" ]; then
      gcc "$c_file_base.c" readMessages.c -o "$OUT_DIR/$c_file_base"
    elif [ "$c_file_base" = "daemon" ]; then
      gcc "$c_file_base.c" readMessages.c grupos.c hashusers.c mailqueue.c -o "$OUT_DIR/$c_file_base"
    elif [ "$c_file_base" = "readMessages" ] ||  [ "$c_file_base" = "hashusers" ] || [ "$c_file_base" = "mailqueue" ] || [ "$c_file_base" = "grupos" ]; then
      :  # Do nothing
    else 
      gcc "$c_file_base.c" -o "$OUT_DIR/$c_file_base"  
    fi
}

# Função para executar um programa
run_program() {
  # Nome do programa (sem extensão)
  program_name="$1"

  # Verifique se o executável existe
  exe_file="$OUT_DIR/$program_name"
  if [ ! -f "$exe_file" ]; then
    echo "Erro: Executável '$program_name' não encontrado."
    return 1
  fi

  # Execute o programa
  "$exe_file"
}

# Função para compilar e executar todos os programas
compile_all() {
  # Navegue no diretório de arquivos C
  for c_file in *.c; do
    # Obtenha o nome do arquivo C (sem extensão)
    c_file_base="${c_file%.c}"

    # Compile o arquivo C
    compile_file "$c_file_base"
  done

  groupadd -f concordia

  chmod u+s $OUT_DIR/concordia-ativar
  chmod u+s $OUT_DIR/concordia-desativar

  if [ ! -p "/tmp/concordia" ]; then
    mkfifo /tmp/concordia
  fi
  chmod 666 /tmp/concordia
  chown :concordia /tmp/concordia

}

is_root
# Execute a função de compilação e execução
compile_all

#run_program "concordia-ativar"