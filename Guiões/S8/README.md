## Questão 1

Para verificarmos as permissões de arquivos e diretorias utilizamos o comando `ls -l`
```
total 0
total 0
-rw-r--r-- 1 zezao zezao 426 Apr 15 10:06 Readme.md
-rw-r--r-- 1 zezao zezao   6 Apr 15 10:05 exemplo.txt
drwxr-xr-x 1 zezao zezao 512 Apr 15 10:06 pasta
```
Para alterar as permissões de um ficheiro usamos o comando `chmod`

```
chmod [quem][operador][permissões] arquivo/diretoria
```

Quem:
- u (propietário)
- g (grupo)
- o (outros)
- a (todos)

Operador:
- \+ (adiciona permissão)
- \- (remove permissão)
- = (define permissão exata)

Permissões:
- r (read)
- w (write)
- x (execute)

Podemos também usar isto em modo octal, por exemplo definir as permissões rw-rw-r-- para o exemplo.txt:
```
chmod 664 exemplo.txt       
```

Já para alterar os propietários e os grupos temos os comandos `chown` e `chgrp`, respetivamente.

O comando `umask` é usado em sistemas Unix/Linux para definir as permissões padrão que serão removidas de novos arquivos e diretorias criados pelo usuário.

## Questão 2

Os novos utilizadores foram criados através do comando ``` sudo adduser [nome] ``` (visto que tivemos problemas na criação e alteração de palavras-passe com o comando useradd)
```
sudo adduser goncalo
sudo adduser ze
```
Com todos os utilizadores para cada membro criados, a criou-se os grupos com os comandos, por exemplo:
```
sudo addgroup grupo
```
E adicionaram-se os utilizadores a esses mesmos grupos com
```
sudo groupadd -g grupo -a goncalo
```




## Questão 3

Criamos um programa em C que recebe um ficheiro como argumento, lê este e imprime o seu conteúdo no stdout.
Assim sendo criamos o executável `imprimir` com: 
```
gcc -o imprimir imprimir.c
```

Criamos um ficheiro ``arquivo.txt`` com conteúdo "Conteúdo do arquivo".
Para testar esta funcionalidade, começamos por definir o propietário do executável sendo apenas a root:
```
sudo chown root imprimir 
sudo chmod 700 imprimir
```
E utilizamos o seguinte comando de forma a atribuir a um usuário os privilégios do propietário do executável:
```
chmod u+s imprimir

```
Assim, imprimir passa a ter nas permissoes no user a flag 's' que deixa aos outros utilizadores a ganhar as propriedades ao correr o programa.

Por fim tentamos correr o programa:
```
$ ./imprime_arquivo arquivo.txt
Conteúdo do arquivo
```

## Questão 4
Enquanto que as permissões padrão do Linux (propietário, grupo e outros) são limitadas ao definir permissões para três categorias de usuários, as ACLs(listas estendidas de controlo de acesso) permitem atribuir permissões específicas para usuários individuais ou grupos.

O comando ``setfacl`` é usado para definir ou modificar as ACLs de um arquivo ou diretoria.

Adicionar permissões de leitura e escrita para um usuário específico:
```
setfacl -m u:usuario:rw arquivo
```
Aplicar alterações recursivamente a uma diretoria:
```
setfacl -R -m u:usuario:rw diretoria
```
Remover permissões de execução para um grupo:
```
setfacl -x g::x arquivo
```
Remover todas as ACLs:
```
setfacl -b exemplo.txt
```

Já o comando `getfacl` serve apenas para mostrar as ACLs correspondentes a um arquivo ou uma diretoria.
```
 ____________
< SSI é fixe >
 ------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```