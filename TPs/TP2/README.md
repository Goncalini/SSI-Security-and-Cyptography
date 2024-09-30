# CONCÓRDIA - Serviço Local de Troca de Mensagens

## Dependências externas necessárias - COMPLETAR

adduser

## Instalação Inicial

Apenas primeiro utilizador, do sistema Linux  local, a iniciar o _Concordia_ deve correr o seguinte comando, os restantes não precisam de o fazer.

``` 
sudo ./install.h
```

## Exemplos de utilização do serviço

Após feita a instalação, pode-se fazer comandos seguintes em qualquer diretoria:

__Ativação do serviço:__ adiciciona o utilizador ao serviço
```
concordia-ativar
```

__Desativação do serviço:__ remove o utilizador do serviço;
```
concordia-desativar
```

__Enviar mensagem__
```
concordia-enviar <nome dest> <msg>
```

__Listar mensagens__
```
concordia-ler <ler <mid>|listar [-a]> 
```

`-a` -> imprime a totalidade das mensagens recebidas


__Ler mensagem__
```
concordia-ler ler <mid>
```

__Responder mensagem:__ responde ao remetente da mensagem com id _mid_
```
concordia-responder <mid> <msg>
```

__Remover mensagem:__ permite remover uma mensagem consoante o id dela (mid) ou todas as mensagens
```
concordia-remover <remover mid|tudo>
```


__Criar Grupo:__ criar um grupo de utilizadores
```
concordia-grupo-criar <nome>
```

__Remover Grupo:__ remover um grupo de utilizadores
```
concordia-grupo-remover <nome>
```

__Listar Membros do Grupo:__
```
concordia-grupo-listar <nome>
```

__Adicionar Membro ao Grupo:__
```
concordia-grupo-adicionar-membro <nome> <uid>
```

__Remover Membro ao Grupo:__
```
concordia-grupo-remover-membro <nome> <uid>
```