from functions import *

def direcionar_requisicao(metodo, caminho, dados, usuario, token):
    retorno = ""
    status = 0
    
    try:
        caminho = caminho.strip("/").split("/")
    except:
        return 400, "caminho inválido"

    if metodo == "GET":
        match caminho[0]:
            case "encomenda":
                status, retorno = exibir_pedidos(caminho, usuario)
            case "produto":
                status, retorno = exibir_produtos(caminho)
            case "info":
                status, retorno = exibir_info(caminho)

    elif metodo == "POST":
        if not isinstance(dados, dict):
            return 400, "dados inválidos"

        match caminho[0]:
            case "encomenda":
                status, retorno = criar_pedido(dados, usuario)
            case "produto":
                status, retorno = criar_produto(dados, usuario)
            case "categoria":
                status, retorno = criar_categoria(dados, usuario)
            case "usuario":
                status, retorno = criar_usuario(dados)
    
    elif metodo == "PATCH":
        if not isinstance(dados, dict):
            return 400, "dados inválidos"

        match caminho[0]:
            case "alterar_senha":
                status, retorno = alterar_senha(dados, usuario)
            case "login":
                status, retorno = login(dados)
            case "logout":
                status, retorno = logout(token)
            case "usuario":
                status, retorno = editar_usuario(dados, usuario)
            case "encomenda":
                status, retorno = editar_pedido(dados, caminho, usuario)
            case "produto":
                status, retorno = editar_produto(dados, caminho, usuario)
            case "info":
                status, retorno = editar_info(dados, usuario)

    elif metodo == "DELETE":
        match caminho[0]:
            case "encomenda":
                status, retorno = remover_pedido(caminho, usuario)
            case "produto":
                status, retorno = remover_produto(caminho, usuario)
            case "categoria":
                status, retorno = remover_categoria(caminho, usuario)
            case "usuario":
                status, retorno = remover_usuario(caminho, dados, usuario)
    
    if status:
        return status, retorno 

    return 404, "caminho não encontrado."