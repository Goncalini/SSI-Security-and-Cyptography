# Relatório - TP1

## Introdução

Este projeto foi realizado em prol da UC de Segurança de Sistemas Informáticos, o mesmo consistiu na implementação de uma aplicação *client-server*, com o objetivo de permitir aos clientes efetuarem diversas trocas de mensagens entre si. A aplicação foi realizada com recurso à linguagem de programação Python e por sua vez utilizamos a biblioteca cryptography que foi ensinada ao longo das aulas práticas.

Essas mesmas mensagens devem possuir proteção quanto a acessos não permitidos de pessoas externas e à manipulação indesejada pelos mesmos, assim como deve possuir autenticidade de forma a que quem recebe as mensagens as possa verificar que quem as enviou foi, de facto, quem disse.

## Arquitetura

O programa está dividido nos seguintes módulos.

- `msg_client.py` -- Cliente, cujo qual pode fazer pedidos através de comandos ao servidor.
- `msg_server.py` -- Servidor, trata dos serviços pedidos e armazenamento das mensagens.
- `validator.py` -- Ficheiro constituído pelas funções responsáveis pela da validação e verificação dos certificados e assinaturas, respetivamente.
- `protocol.py` -- Ficheiro que define a _Class Protocol_, a mesma possui os métodos responsáveis pela construção do protocolo das mensagens que vão ser trocadas entre cliente e servidor.
- `utils.py` -- Módulo com as funções que irão tratar do *parsing* e verificação dos comandos e das mensagens.

### Acordo de chaves Diffie-Hellman e validação de certificados

De forma a responder ao pretendido pelo enunciado, decidimos recorrer à utilização do protocolo de acordo de chaves *Diffie-Hellman*, de forma a que as mensagens criptografadas fossem o mais seguras possível e difíceis de aceder ilegitimamente. Para isso, inicialmente o cliente e o servidor precisam de concordar sobre uma chave sem revelar a mesma.

Para isso o cliente e o servidor começam por gerar as suas chaves privadas e públicas. O cliente envia primeiro ao servidor a sua chave pública, onde o mesmo responde com a sua chave pública, uma assinatura do par da sua chave pública com a recebida pelo cliente e o seu certificado. Com isto, o cliente é capaz de validar o certificado e a assinatura. Se a validação der o esperado, o cliente poderá confiar na chave pública recebida, gerando, em conjunto com a sua chave privada, um segredo partilhado. Por sua vez o cliente envia ao servidor também o seu certificado e a assinatura do par de chaves públicas, repetindo o processo no lado do servidor.

Vale realçar que para tratar da encriptação de mensagens foi usado o algoritmo *AES-GCM*, conjugando o mesmo com a derivação da chave partilhada usando *HKDF*.


## Instruções de uso

### Inicialização do cliente

O Cliente deve ser inicializado passando o certificado a ser usado como argumento após `-user`, sendo os possíveis `MSG_CLI1.p12`, `MSG_CLI2.p12` e `MSG_CLI3.p12`.

Se nada for passado como argumento ele irá inicializar o programa usando como certificado `MSG_CLI1.p12`.

O cliente ao ser inicializado é lhe atribuido um `UID`, sendo esse obtido a partir do `PSEUDONYM` contido no certificado que lhe é passado.

#### Exemplo de inicialização de cliente

`python3 msg_client.py -user MSG_CLI3.p12 `

### Send

O comando `send` deve ser utilizado passando como argumentos o `<UID>` e o `<SUBJECT>`.

Este comando é responsável por enviar as mensagens escolhidas para o servidor, onde as mesmas são armazenadas num dicionário global denominado por `queues`, a estrutura desse dicionário é a seguinte:

```
Queues = { UID : [(Msg1, Flag), (Msg2, Flag), ...] } 
# Sendo esta Flag, um booleano que representa se a mensagem já foi lida ou não.
```

As mensagens enviadas estão armazenadas em objetos da _Class Protocol_ que guarda o *certificado*, a *assinatura*, o *UID do sender*, o *UID do destino*, o *timestamp*, o *assunto* e o *conteúdo da mensagem*.

A mensagem chegando ao servidor é decomposta antes de ser armazenada, sendo importante realçar que, nesta fase, é o servidor o responsável pela atribuição do devido *timestamp* da mensagem!

#### Exemplo de uso do send

```
>>>send MSG_CLI2 ola
Input message to send (empty to finish)
>>>Mundo
Message sent.

```

### Askqueue

Comando sem argumentos, responsável por apresentar a lista de mensagem não lidas que cliente possui. A lógica de como o comando funciona será explicada mais à frente juntamente com o `getmsg`, por ambos serem extremamente parecidos.

Caso não haja mensagens irá ser imprimido para o strderr `You don't have any messages.`

Caso todas as mensagens tenham já sido lidas será imprimido `You don't have any unread messages.`

#### Exemplo de uso do askqueue

```
>>>askqueue
Message: 0, From: MSG_CLI1, Subject: ola, Time: 2024-04-05 16:10:20
```



### Getmsg

Este recebe como argumento o número da mensagem que quer receber, após o cliente enviar esse comando, obviamente encriptado, ao servidor, à semelhança do `askqueue`, o servidor executa a devida função e constrói a mensagem com as informações pedidas pelo cliente. Essa é enviada ao cliente que após desencriptada e decomposta é instruída a apresentar no terminal as devidas informações, no caso do `getmsg` essas são: o *sender*, o *timestamp*, o *assunto* e o *conteúdo*. No caso da mensagem não existir na queue do utilizador, a aplicação emitirá `MSG RELAY SERVICE: unknown message!`

Importante denotar que as mensagens possuem nelas o certificado e assinatura do *sender*, de forma a que o cliente que recebe a mensagem verifique e valide o certificado e a assinatura, para por sua vez conseguir concluir que a mensagem foi enviada por quem diz que enviou e não está ninguém a se fazer passar pelo *sender*.

No caso da verificação falhar, ira ser emitido o erro `MSG RELAY SERVICE: verification error!`


#### Exemplo de uso do getmsg

```
>>>getmsg 0
<Name(C=PT,ST=Minho,L=Braga,O=Universidade do Minho,OU=SSI MSG RELAY SERVICE,CN=User 1 (SSI MSG Relay Client), 2.5.4.65=MSG_CLI1)>
Sender certificate is valid
Signature is valid, sender is trustworthy
From: MSG_CLI1
Time: 2024-04-05 16:10:20
Subject: ola
Message: Mundo

```

### Help

O `help` é o comando que imprime as instruções de uso do programa.

#### Exemplo de uso do help

```
>>help

Bem-vindo ao CypherLink!
Instruções de uso: python3 msg_client.py [opções]
   -user <FNAME>:  Especificar um ficheiro keystore para o utilizador (opcional)
   send <UID> <SUBJECT>:  Enviar uma mensagem com assunto <SUBJECT> para o utilizador <UID>
   askqueue: Listar as mensagens não lidas.
   getmsg <NUM>: Pedir ao servidor o envio da mensagem com número <NUM> na queue.
   help: Exibe esta mensagem de ajuda.
   quit: Encerra a sessão do usuário.
```

### Quit

Termina a execução do cliente.

```
>>>quit
Socket closed!
```

## Informações extras relevantes

Graças ao uso de um dicionário global, é possivel enviar mensagens para clientes *offline* desde que esse se tenha autenticado anteriormente.

Foi implmentado um pequeno sistema de logs como auxílio parar conseguirmos verificar e atestar que os comandos foram executados e submetidos ao sistema.

O grupo desenvolveu também um script para a geração dos próprios certificados, mas como iria levar a mudanças substanciais na arquitetura e por falta de tempo de conseguir resolver essas mudanças todas, esta funcionalidade acabou por não ser implementada.

O mesmo aconteceu para "Possibilitar o envio de mensagens com garantias de confidencialidade mesmo perante um servidor “curioso”", apesar de termos pensado numa estratégia que tentamos implementar, mas com a falta de tempo e as mudanças drásticas na arquitetura, não ficou pronto a tempo.


Essa estratégia consistia em:

- Gerar uma chave aleatória

- Encriptar o conteúdo da mensagem com essa chave

- Encriptar a chave gerada com a chave pública do certificado do destino, desta forma só a chave privada do certificado destino poderia desencriptar a chave gerada

- Após o destino desencriptar a chave, usaria a mesma para desencriptar a mensagem

- Claro que tratando das devidas validações durante este processo



## Conclusão

Ao longo do desenvolvimento deste projeto fomos capazes de pôr em prática as diversas estratégias de criptografia aplicada estudadas ao longo das aulas teórico-práticas. O desenvolvimento foi realizado com bastante delicadeza e cuidado para que respondesse ao que o enunciado pretendia e, além disso, permitiu aprender como construir
uma aplicação de troca de mensagens *client-server* e vice-versa que possamos confiar.

Desta forma fomos capazes de aprofundar e consolidar a matéria, tanto no funcionalismo de um programa *client-server* como na área de criptografia aplicada, principalmente como o uso dos algoritmos de encriptação, o acordo e derivação de chaves e o uso de certificados, como por exemplo o x509, contribuem e fornecem para a confidencialidade e a segurança das mensagens e de dados de forma quase garantida. 

Por fim, reconhecemos que estes conhecimentos serão bastante úteis para o futuro da nossa carreira como desenvolvedores e a elaboração deste trabalho-prático mostrou que ainda há muito que explorar e aprofundar nesta área!


