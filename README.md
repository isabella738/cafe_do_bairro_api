# API Cafe do Bairro
API para aplicativo de organização de encomendas de uma padaria.  

## Visão Geral
O programa é escrito em python (compatível com versões a partir da 3.10). Para rodar o servidor, basta baixar o arquivo do projeto e e executar o arquivo .main.py.  
Na memória principal, os dados são organizados em listas de dicionários, que guardam encomendas, produtos e usuários.

### Produtos (/produto)
No código, produtos e itens são usados como sinônimos.  
Um item contém:
- Nome
- Categoria
- Valor
- Status
- Descrição
- Código

Código é um identificador único de 5 caracteres aleatórios.  
Status pode assumir o valor 1 (produto disponível) ou 0 (produto temporariamente indisponível)

### Usuários (/usuario)
Usuários contém nome (que vale como código identificador), senha e "adm", que indica se o usuário tem permissão para fazer determinadas ações.  

Um administrador consegue criar/editar produtos e categorias, ver todos os pedidos e alterar campos específicos de encomendas e usuários. Consegue também tornar outros usuários administradores e remover usuários se necessário. Fora isso, só pode editar campos relacionados ao próprio perfil. Além disso, consegue remover pedidos e categorias, mas não pode remover algum item se ele pertencer a algum pedido.  

### Encomendas (/encomenda)
No código, encomendas e pedidos são usados como sinônimos.  
Uma encomenda contém:
- Nome do usuário que a fez
- Telefone
- Prazo
- Itens
- Comentário
- Status
- Código
  
Código é um identificador único de 5 caracteres aleatórios.  

Status pode assumir o valor 0 (pedido enviado), 1 (pedido aceito), 2 (em preparo) e 3 (concluído). O último estágio de uma encomenda, quando ela for entregue, é simplesmente a remoção dela da lista.  

O prazo diz respeito a ano, mês e dia, sem incluir hora. Não é permitido marcar mais de 5 bolos para um dia. Essa condição verifica itens e não número de encomendas, pois uma encomenda pode ter mais de um item.  

Aqui, os itens são guardados como uma lista de códigos dos produtos, não as informações deles em si. Se são encomendadas duas unidades de um mesmo item, ele aparece duas vezes na lista como produtos "diferentes".  

O campo comentário é opcional. É uma forma prática de fazer uma observação sobre o pedido sem precisar ir diretamente no whatsapp. Dessa forma, a comunicação direta só precisa ser feita para dúvidas específicas ou algum imprevisto, etc.  

Por fim, os clientes só podem alterar algum campo da encomenda com 24 horas de antecendência, que é mais ou menos o tempo que dona Marta consegue montar um pedido. Supõe-se que exceções e urgências sejam reportadas diretamente via whatsapp.  

### Outros Dados
'info' (/info) é um dicionário que guarda informações essenciais relacionadas à dona Marta (nome, telefone, endereço). É uma forma prática de resgatar essas informações no front-end, por exemplo.  

'categorias' (/categoria) é uma lista de strings. Surgiu da necessidade de identificar quais itens em um pedido eram bolos na hora de validar as vagas para um dia. Fora isso, é totalmente cosmético.  

'tokens' é um dicionário que guarda tokens de acesso relacionados a um usuário. No início de cada sessão, um token de 5 caracteres aleatórios é gerado e associado ao nome do usuário. Estes tokens são armazenados temporariamente num dicionário durante a execução do servidor. Dessa forma, diferentes usuários podem acessar o servidor ao mesmo tempo sob suas próprias condições.  

## Funcionalidades
Basicamente, requisições são feitas para os dados descritos acima (tirando tokens) e, por padrão, seguem o mesmo início de URL (especificado para cada dado acima nos parênteses), mudando só o verbo. Salvo algumas requisições especiais.  
Sem uma sessão iniciada, só é possível fazer a ação de visualizar itens e informações da padaria. O resto fica bloqueado.   

### 1. Listar (GET)
É possível listar pedidos, itens e informações da padaria. É possível, se necessário, filtrar os resultados no próprio caminho. Por exemplo, GET /produto/categoria/bolo retorna somente os itens na categoria bolo e GET /encomenda/codigo/00001 retorna a encomenda de código 00001, se existir, mas GET /produto retorna a lista de todos os produtos.  

### 2. Criar (POST)
É possível criar novo pedido, item, categoria e usuário. Criar item e categoria é exclusivo de administradores.  
É esperado que o cliente envie apenas em formato .json as informações do novo resurso.  

### 3. Atualizar (PATCH)
Atualizar significa modificar alguma informação de usuário, item, pedido ou informação da padaria. O caminho especifica qual objeto vai ser alterado (ou seja, só importa para item e pedido). É esperado que os campos a serem alterados sejam enviados em formato json.  

Somente administradores podem alterar itens, informações da padaria, o status de um pedido e a flag de um usuário. Fora isso, somente o dono do pedido ou perfil consegue alterar suas informações.  

Além disso, PATCH contempla as funções de login (ler e validar nome e senha, então criar um token de acesso), logout (remover o token de acesso) e o campo de redefinir senha, que recebe uma função à parte pois passa por uma etapa extra de validação.   

### 4. Remover (DELETE)
É possível remover pedido, produto, usuário e categoria (que não seja 'outros'). De forma semelhante ao GET, só precisa passar pelo URL o elemento a ser removido, salvo a remoção de usuario, pois precisa confirmar a senha. Somente administradores podem remover produtos e categorias. Eles também podem remover usuários sem precisar de uma autorização.  

Remover pedido pode ser feito por um administrador para finalizar ou recusar um pedido. A ideia é que, ao recusar, exista um campo no aplicativo para descrever o ocorrido e enviar a mensagem diretamente ao cliente por whatsapp ou sms, já que o único meio de contato cadastrado é o telefone. Acredito que esta mecânica seja muito complexa de implementar, então não existe explicitamente no código.  

Remover pedido pode ser feito também por um não administrador para cancelá-lo. Porém, está sujeito à mesma condição de não poder modificar um pedido a menos de 24 horas do prazo.  

## Sobre o Código
O backend é separado em 6 arquivos:
- variables.py: declaração das principais variáveis de listas e dicionários descritas anteriormente.
- save.py: funções de salvar e carregar dados, além de validar usuario pelo token.
- endpoints.py: onde ocorre as principais ações do servidor, para cada endpoint
- auxiliary.py: funções auxiliares para endpoints, como validação de entrada.
- direcionamento.py: define as funções a serem executadas com base na requisição do cliente.
- .main.py: onde o servidor é iniciado.   

Os dados são guardados na subpasta 'dados' em json ou txt dedicados para cada tipo de dado. No momento eles possuem conteúdo, meramente ilustrativo, e podem sre apagados se quiser. Mas, preferencialmente, não apague o usuário 'Marta' nem 'MaridoDeMarta', que são os únicos administradores. Um usuário só pode se tornar adm através de outro adm, a não ser que seja alterado diretamente no arquivo.  

### Pontos Fracos
1. Não existe criptografia de senhas e tokens, nem tráfego seguro de dados. Além de que não há verificação de endereço de IP, então inúmeras tentativas de login podem ser feitas por segundo.
2. É possível que existam erros de typerror, por exemplo, se tentar fazer uma requisição muito fora da curva.
3. A não ser que o servidor seja reiniciado ou o usuário deslogado ou removido, o token de acesso fica válido eternamente.
4. O identificador do usuário é seu próprio nome.
5. Dentre outros pormenores.

Vale ressaltar que este é o primeiro projeto de API que faço, é um formato que não estou acostumada, mas fiz o possível para ficar minimamente usável  
Valeu ;)
