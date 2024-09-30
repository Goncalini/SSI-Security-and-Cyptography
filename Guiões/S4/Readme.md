## Questão 2
Em primeiro lugar ao utilizar um NONCE fixo, este vai perder a propiedade de unicidade, ou seja, já não pode ser usado em múltiplas mensagens. Para além disso quando se usa um NONCE fixo com uma chave específica, estes vão gerar fluxos de chave repetidos, o que significa que no caso de um atacante observr os dois conjuntos de mensagens cifradas, ele pode realizar *known-plaintext attack*.

## Questão 3
Utilizar o programa *chacha20_int_attck.py* nas versões AES usando CBC ou CTR não tem impacto direto com nenhum deles, pois ao contrário do chacha20, estas duas versões utilizam o método de cifra por blocos em vez de cifras sequenciais.