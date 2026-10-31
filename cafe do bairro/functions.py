from auxiliary import *
import variables as v

# GET
def exibir_pedidos(caminho):
    if not v.lista_pedidos:
        return 403, "lista vazia."

    v.lista_pedidos.sort(key=lambda item: item["prazo"])

    chave = caminho[1] if len(caminho) > 1 else None
    conteudo = caminho[2] if len(caminho) > 2 else None

    if not chave:
        return 200, v.lista_pedidos
    
    if chave and conteudo is None:
        return 400, "falta conteúdo."
    
    if chave in v.lista_pedidos[0]:
        lista = [i for i in v.lista_pedidos if i[chave] == conteudo]
        return 200, lista

    return 404, "chave não encontrada."

def exibir_produtos(caminho):
    if not v.lista_itens:
        return 403, "lista vazia."

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
    chave = caminho[1] if len(caminho) > 1 else None

    if not chave:
        return 200, v.info
        
    if chave in v.info:
        return 200, v.info[chave]

    return 404, "chave não encontrada."

# POST
def criar_pedido(dados):
    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    mensagens = []

    # nome do cliente
    nome = dados.get("nome")
    mensagens.append(verificar_string(nome))

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

    # envio de erros
    erros = [m for m in mensagens if m != ""]
    if erros:
        return 400, erros
    
    # verifica se o pedido respeita o limite do dia
    if (erro := disponibilidade(prazo, itens, None)):
        return 403, erro

    # montar pedido
    pedido = {
        "nome": nome,
        "telefone": telefone,
        "prazo": prazo,
        "itens": itens,
        "comentario": comentario,
        "status": 0,
        "codigo": gerar_codigo(v.lista_pedidos)
    }

    v.lista_pedidos.append(pedido)
    return 201, pedido

def criar_produto(dados):
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

def criar_categoria(dados):
    if not isinstance(dados, dict):
        return 400, "dados em formato inválido."

    novo = dados.get("categoria")

    if (erro := verificar_string(novo)):
        return 400, erro

    if novo in v.categorias:
        return 400, "categoria já existe."

    v.categorias.append(novo)
    return 201, novo

# PATCH
def editar_pedido(dados, caminho):
    if not v.lista_pedidos:
        return 403, "lista vazia."

    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for pedido in v.lista_pedidos:
        if codigo == pedido["codigo"]:

            novo = pedido.copy()
            for chave, conteudo in dados.items():
                
                erro = ""
                match chave:
                    case "telefone":
                        erro = verificar_telefone(conteudo)
                    case "nome":
                        erro = verificar_string(conteudo)
                    case "prazo":
                        erro = verificar_data(conteudo) or disponibilidade(conteudo, pedido["itens"], None)
                    case "itens":
                        erro = verificar_pedido(conteudo, v.lista_itens) or disponibilidade(pedido["prazo"], conteudo, pedido)
                    case "status":
                        erro = verificar_int(conteudo, 0, 3)
                    case "comentario":
                        pass
                    case "codigo":
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

def editar_produto(dados, caminho):
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
                        pass
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

def editar_info(dados):
    for chave, conteudo in dados.items():

        if chave in v.info:
            v.info[chave] = conteudo
        else:
            return 404, "campo não encontrado."
    
    return 204, ""

# DELETE
def remover_pedido(caminho):
    if not v.lista_pedidos:
        return 403, "lista vazia."

    codigo = caminho[1] if len(caminho) > 1 else None

    if (erro := verificar_string(codigo)):
        return 400, erro

    for pedido in v.lista_pedidos:
        if codigo == pedido["codigo"]:
            v.lista_pedidos.remove(pedido)
            return 204, ""
    
    return 404, "pedido não encontrado."

def remover_produto(caminho):
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

def remover_categoria(caminho):
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

