from auxiliary import *
import variables as v

# GET
def exibir_pedidos(caminho, usuario):
    # Usuários não adms só podem ver seus próprios pedidos

    if not usuario:
        return 400, "sessão não iniciada."

    if not v.lista_pedidos:
        return 200, []

    chave = caminho[1] if len(caminho) > 1 else None
    conteudo = caminho[2] if len(caminho) > 2 else None

    if chave and conteudo is None:
        return 400, "falta conteúdo."

    v.lista_pedidos.sort(key=lambda item: item["prazo"])

    # se não for administrador
    if not usuario["adm"]:
        lista_filtrada = [i for i in v.lista_pedidos if i["usuario"] == usuario["nome"]]

        if not chave:
            return 200, lista_filtrada
            
        if chave in v.lista_pedidos[0]:
            lista = [i for i in lista_filtrada if i[chave] == conteudo]
            return 200, lista

        return 404, "chave não encontrada."

    # se for administador
    if not chave:
        return 200, v.lista_pedidos
    
    if chave in v.lista_pedidos[0]:
        lista = [i for i in v.lista_pedidos if i[chave] == conteudo]
        return 200, lista

    return 404, "chave não encontrada."

def exibir_produtos(caminho):
    # Não depende do usuário

    if not v.lista_itens:
        return 200, []

    chave = caminho[1] if len(caminho) > 1 else None
    conteudo = caminho[2] if len(caminho) > 2 else None

    if not chave:
        return 200, v.lista_itens
    
    if chave and conteudo is None:
        return 400, "falta conteúdo."
    
    if chave in v.lista_itens[0]:
        lista = [i for i in v.lista_itens if i[chave] == conteudo]
        return 200, lista

    return 404, "chave não encontrada."

def exibir_info(caminho):
    # Não depende do usuário

    chave = caminho[1] if len(caminho) > 1 else None

    if not chave:
        return 200, v.info
        
    if chave in v.info:
        return 200, v.info[chave]

    return 404, "chave não encontrada."

# POST
def criar_pedido(dados, usuario):
    # Livre para qualquer usuário

    if not usuario:
        return 400, "sessão não iniciada."

    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    mensagens = []

    # numero de telefone
    telefone = dados.get("telefone")
    mensagens.append(verificar_telefone(telefone))

    # data de entrega
    prazo = dados.get("prazo")
    mensagens.append(verificar_data(prazo))

    # itens do pedido
    itens = dados.get("itens")
    mensagens.append(verificar_pedido(itens, v.lista_itens))

    # observações sobre o pedido, se houver
    comentario = dados.get("comentario")
    if not comentario is None:
        mensagens.append(verificar_string(comentario))

    # envio de erros
    erros = [m for m in mensagens if m != ""]
    if erros:
        return 400, erros
    
    # verifica se o pedido respeita o limite do dia
    if (erro := disponibilidade(prazo, itens, None)):
        return 403, erro

    # montar pedido
    pedido = {
        "nome": usuario["nome"],
        "telefone": telefone,
        "prazo": prazo,
        "itens": itens,
        "comentario": comentario,
        "status": 0,
        "codigo": gerar_codigo(v.lista_pedidos)
    }

    v.lista_pedidos.append(pedido)
    return 201, pedido

def criar_produto(dados, usuario):
    # Somente para adms.

    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    mensagens = []

    # nome do produto
    nome = dados.get("nome")
    mensagens.append(verificar_string(nome))

    # valor do produto
    valor = dados.get("valor")
    mensagens.append(verificar_valor(valor))

    # categoria do produto
    categoria = dados.get("categoria")
    mensagens.append(pertence(categoria, v.categorias))

    # descricao do produto
    descricao = dados.get("descricao")
    if not descricao is None:
        mensagens.append(verificar_string(descricao))

    # envio de erros
    erros = [m for m in mensagens if m != ""]
    if erros:
        return 400, erros
    
    # montar o item
    item = {
        "nome": nome,
        "categoria": categoria,
        "valor": valor,
        "descricao": descricao,
        "status": 1,
        "codigo": gerar_codigo(v.lista_itens)
    }

    v.lista_itens.append(item)
    return 201, item

def criar_categoria(dados, usuario):
    # Somente para adms.

    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    novo = dados.get("categoria")

    if (erro := verificar_string(novo)):
        return 400, erro

    if novo in v.categorias:
        return 400, "categoria já existe."

    v.categorias.append(novo)
    return 201, novo

def criar_usuario(dados):
    # Livre para qualquer usuário

    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    mensagens = []

    nome = dados.get("nome")
    mensagens.append(verificar_string(nome))

    senha = dados.get("senha")
    mensagens.append(verificar_string(senha))

    # envio de erros
    erros = [m for m in mensagens if m != ""]
    if erros:
        return 400, erros
    
    if usuario_existe(nome):
        return 403, "este nome já está em uso."

    user = {
        "nome": nome,
        "senha": senha,
        "adm": 0,
    }
    
    v.usuarios.append(user)
    return 204, ""


# PATCH
def alterar_senha(dados, usuario):
    # Altera a senha a partir de uma confirmação da atual.

    if not usuario:
        return 400, "sem sessão iniciada."

    confirmacao = dados.get("confirmacao")
    novo = dados.get("nova_senha")

    if (erro := verificar_string(novo)):
        return 400, erro
    
    if usuario["senha"] != confirmacao:
        return 403, "senhas não coincidem."
    
    usuario["senha"] = novo
    return 204, ""

def login(dados):
    # Cria um token se nome e senha estiverem corretos.

    nome = dados.get("nome")
    senha = dados.get("senha")
    if (erro := verificar_string(senha)) or (erro := verificar_string(nome)):
        return 400, erro

    for user in v.usuarios:
        if user["nome"] == nome:
            if user["senha"] == senha:
                token = gerar_codigo(v.tokens)
                v.tokens[token] = user["nome"]
                return 200, {"token":token}
            
            return 400, "senha inválida."
        
    return 404, "usuário não encontrado."

def logout(token):
    # Somente apaga o token (1 sessão), não todas as sessões do usuário.

    if token in v.tokens:
        del v.tokens[token]
        return 204, ""
    return 404, "não encontrado."

def editar_usuario(dados, usuario):
    # Praticamente, serve só para adms que querem mudar a flag de adm de outro usuário,
    # pois o nome funciona como código e senha é editada em outro caminho, mas tá aí 
    # qualquer coisa

    if not usuario:
        return 400, "sessão não iniciada."
    
    for user in v.usuarios:
        if user == usuario:

            novo = user.copy()
            for chave, conteudo in dados.items():

                erro = ""
                match chave:
                    case "nome":
                        return 403, "campo não editável"
                    case "senha": 
                        return 403, "caminho errado para a ação."
                    case "adm":
                        if not usuario["adm"]:
                            return 403, "não tem permissão para essa ação."
                        erro = verificar_string(conteudo, 0, 1)
                    case _:
                        return 404, "campo não encotrado."
                
                if not erro:
                    novo[chave] = conteudo
                else:
                    return 400, erro
            
            user.update(novo)
            return 204, ""
    
    return 404, "usuario não encontrado."

def editar_pedido(dados, caminho, usuario):
    # Não administradores não podem editar/cancelar um pedido se o prazo terminar
    # em menos de 24 horas.

    if not usuario:
        return 400, "sessão não iniciada."

    if not v.lista_pedidos:
        return 403, "lista vazia."
    
    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for pedido in v.lista_pedidos:
        # Tirando o status, somente os donos dos proprios pedidos podem alterar um campo dele

        if codigo == pedido["codigo"]:

            # Bloqueios de não administradores
            if not usuario["adm"]:
                if pedido["nome"] != usuario["nome"]:
                    return 403, "sem permissão para realizar esta ação."
                
                if horas_ate(pedido["prazo"]) <= 24:
                    return 403, "pedidos devem ser alterados com até 24 horas de antecedência."

            # Mudanças de fato
            novo = pedido.copy()
            for chave, conteudo in dados.items():

                if chave != status:
                    if pedido["nome"] != usuario["nome"]:
                        return 403, "sem permissão para realizar esta ação."
                
                erro = ""
                match chave:
                    case "telefone":
                        erro = verificar_telefone(conteudo)
                    case "prazo":
                        erro = verificar_data(conteudo) or disponibilidade(conteudo, pedido["itens"], None)
                    case "itens":
                        erro = verificar_pedido(conteudo, v.lista_itens) or disponibilidade(pedido["prazo"], conteudo, pedido)
                    case "comentario":
                        if not conteudo is None:
                            erro = verificar_string(conteudo)
                    case "status":
                        if not usuario["adm"]:
                            return 403, "sem permissão para esta ação."
                        erro = verificar_int(conteudo, 0, 3)
                    case "codigo":
                        return 403, "campo não é editável."
                    case "nome":
                        return 403, "campo não é editável."
                    case _:
                        return 404, "um ou mais campos informados não existem."
                
                if not erro:
                    novo[chave] = conteudo
                else:
                    return 400, erro
            
            pedido.update(novo)
            return 204, ""

    return 404, "pedido não encontrado."

def editar_produto(dados, caminho, usuario):
    # Somente para adm.

    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    if not v.lista_itens:
        return 403, "lista vazia."

    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for item in v.lista_itens:
        if codigo == item["codigo"]:

            novo = item.copy()
            for chave, conteudo in dados.items():
                
                erro = ""
                match chave:
                    case "nome":
                        erro = verificar_string(conteudo)
                    case "categoria":
                        erro = verificar_string(conteudo) or pertence(conteudo, v.categorias)
                    case "valor":
                        erro = verificar_valor(conteudo)
                    case "status":
                        erro = verificar_int(conteudo, 0, 1)
                    case "descricao":
                        if not conteudo is None:
                            erro = verificar_string(conteudo)
                    case "codigo":
                        return 403, "campo não é editável."
                    case _:
                        return 404, "um ou mais campos informados não existem."
                
                if not erro:
                    novo[chave] = conteudo
                else:
                    return 400, erro
            
            item.update(novo)
            return 204, ""

    return 404, "item não encontrado."

def editar_info(dados, usuario):
    # Somente para adm. Os campos são fixos.

    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    for chave, conteudo in dados.items():

        if chave in v.info:
            v.info[chave] = conteudo
        else:
            return 404, "campo não encontrado."
    
    return 204, ""


# DELETE
def remover_pedido(caminho, usuario):
    # Para situações de cancelamento, conclusão ou recusa de pedido

    if not usuario:
        return 400, "sessão não iniciada."

    if not v.lista_pedidos:
        return 403, "lista vazia."

    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for pedido in v.lista_pedidos:
        if codigo == pedido["codigo"]:

            # bloqueios de não administradores
            if not usuario["adm"]:
                if pedido["nome"] != usuario["nome"]:
                    return 403, "sem permissão para realizar esta ação."
                
                if horas_ate(pedido["prazo"]) <= 24:
                    return 403, "pedidos devem ser alterados com até 24 horas de antecedência."                    

            # 
            v.lista_pedidos.remove(pedido)
            return 204, ""
    
    return 404, "pedido não encontrado."

def remover_produto(caminho, usuario):
    # Somente para adms. A ação é bloqueada se existirem pedidos com o item.

    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    if not v.lista_itens:
        return 403, "lista vazia."

    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for pedido in v.lista_pedidos:
        if any(codigo == i for i in pedido["itens"]):
            return 403, "existem pedidos ativos com este item."

    for item in v.lista_itens:
        if codigo == item["codigo"]:
    
            v.lista_itens.remove(item)
            return 204, ""
    
    return 404, "produto não encontrado."

def remover_categoria(caminho, usuario):
    # Somente para adms. "Outros" não é removível.
    if not usuario:
        return 400, "sessão não iniciada."

    if not usuario["adm"]:
        return 403, "sem permissão para esta ação"

    categoria = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(categoria)):
        return 400, erro

    if not categoria in v.categorias:
        return 404, "categoria não encontrada."
    
    if categoria == "outros":
        return 403, "categoria não removível."
    
    for item in v.lista_itens:
        if item["categoria"] == categoria:
            item["categoria"] = "outros"

    v.categorias.remove(categoria)

    return 204, ""

def remover_usuario(caminho, dados, usuario):
    # Administradores podem remover qualquer usuário.

    if not usuario:
        return 400, "sessão não iniciada."

    nome = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(nome)):
        return 400, erro

    # Caso um não adm queira remover um outro usuário
    if not usuario["adm"]:
        if nome != usuario["nome"]:
            return 403, "sem permissão para realizar esta ação."
    
    #
    for user in v.usuarios:
        if user["nome"] == nome:
            
            # Se não é adm, precisa confirmar a senha
            if not usuario["adm"]:
                confirmacao = dados.get("confirmacao")
                if confirmacao != user["senha"]:
                    return 403, "senhas não coincidem."

            # Excluir pedidos no nome desta pessoa
            v.lista_pedidos = [i for i in v.lista_pedidos if pedido["nome"] != nome]

            # Deslogar todas as sessões no nome deste usuario
            for token, nome_usuario in list(v.tokens.items()):
                if nome_usuario == user["nome"]:
                    logout(token)
            
            v.usuarios.remove(user)
            return 204, ""
    
    return 404, "usuario não encontrado."