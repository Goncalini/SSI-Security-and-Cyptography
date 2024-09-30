## Questão 1
As diferenças no comportamento dos dois programs não foram notórias.

## Questão 2
A cifra one-time pad é considerada segura quando verificamos as seguintes condições, a chave utilizada na cifra one-time pad é uma sequência de bits totalmente aleatória e não previsível, uma chave deve ser usada para decifrar apenas uma única mensagem e o tamanho da chave deve ter exatamente o tamanho da mensagem.
Se essas condições forem satisfeitas, a cifra one-time pad garante-nos segurança absoluta. Porém no bad otp,graças ao random.randbytes(n), que utiliza sempre a mesma seed em todas as chamadas da função, isto torna a geração da chave deterministica e previsível, ou seja, é suscetível a ataques.