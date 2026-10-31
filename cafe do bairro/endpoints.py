from functions import *

def direcionar_requisicao(metodo, caminho, dados):
    retorno = ""
    status = 0
    
    try:
        caminho = caminho.strip("/").split("/")
    except:
        return 400, "caminho inválido"

    if metodo == "GET":
        match caminho[0]:
            case "encomenda":
                status, retorno = exibir_pedidos(caminho)
            case "produto":
                status, retorno = exibir_produtos(caminho)
            case "info":
                status, retorno = exibir_info(caminho)

    elif metodo == "POST":
        if not isinstance(dados, dict):
            return 400, "dados inválidos"

        match caminho[0]:
            case "encomenda":
                status, retorno = criar_pedido(dados)
            case "produto":
                status, retorno = criar_produto(dados)
            case "categoria":
                status, retorno = criar_categoria(dados)
    
    elif metodo == "PATCH":
        if not isinstance(dados, dict):
            return 400, "dados inválidos"

        match caminho[0]:
            case "encomenda":
                status, retorno = editar_pedido(dados, caminho)
            case "produto":
                status, retorno = editar_produto(dados, caminho)
            case "info":
                status, retorno = editar_info(dados)

    elif metodo == "DELETE":
        match caminho[0]:
            case "encomenda":
                status, retorno = remover_pedido(caminho)
            case "produto":
                status, retorno = remover_produto(caminho)
            case "categoria":
                status, retorno = remover_categoria(caminho)
    
    if status:
        return status, retorno 

    return 404, "caminho não encontrado."