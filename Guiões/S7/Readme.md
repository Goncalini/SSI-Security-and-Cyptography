## Questão 1

Em primeiro lugar, ambas as chaves em si têm de ser válidas. 
Como par de chaves, estas devem estar no formato PEM ou DER. O par de chaves deve ter os mesmos parâmetros, (módulo, expoente público). E, por fim, para de facto termos a certeza que é um par de chaves válido, podemos realizar um teste de criptografia assimétrica, ou seja, cifrar uma mensagem com a chave pública e, em seguida, decifrá-la com a chave privada, de forma a verificar se conseguimos recuperar a mensagem original, caso consigamos o par de chaves é válido.

## Questão 2

Durante o processo de validação achamos que os campos que merecem mais atenção são: 

- **Issuer e Subject**: Mostra-nos se o emissor do certificado é confiável e se o assunto corresponde à entidade esperada.

- **Validity**: Mostra-nos o período de tempo em que o certificado é válido.

- **Subject Public Key Info**: Este campo descreve o algoritmo de chave pública utilizado e a própria chave pública, o que nos pode garantir que a chave pública é válida e se corresponde à chave privada associada.

- **Signature Algorithm**: Este campo indica-nos qual o algoritmo utilizado para assinar o certificado e a própria assinatura.