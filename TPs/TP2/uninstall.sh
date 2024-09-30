
OUT_DIR="/usr/bin"

is_root() {
  if [ "$(whoami)" = "root" ]; then
    true
  else
    echo "Este script deve ser executado como root."
    exit 1
  fi
}

# Função para desinstalar programas
uninstall_all() {
  # Lista todos os arquivos no diretório de saída
  for exe_file in "$OUT_DIR"/*; do
    # Verifica se é um arquivo regular
    if [ -f "$exe_file" ]; then
        if [[ "$file" == *.o ]] || [[ "$file" == *concordia-ativar ]] || [[ "$file" == *concordia-ler ]] || [[ "$file" == *concordia-desativar ]]; then
            # Remove o executável
            rm -f "$exe_file"
            echo "Desinstalado: $exe_file"
        fi
    fi
  done
}

is_root
uninstall_all