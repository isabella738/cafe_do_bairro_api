import variables as v
import json

def salvar_dados():
    try:        
        with open("dados/itens.json", "w", encoding="utf-8") as arquivo:
            json.dump(v.lista_itens, arquivo, ensure_ascii=False, indent=4)

        with open("dados/pedidos.json", "w", encoding="utf-8") as arquivo:
            json.dump(v.lista_pedidos, arquivo, ensure_ascii=False, indent=4)

        with open("dados/info.json", "w", encoding="utf-8") as arquivo:
            json.dump(v.info, arquivo, ensure_ascii=False, indent=4)

        with open("dados/usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(v.usuarios, arquivo, ensure_ascii=False, indent=4)

        with open("dados/categorias.txt", "w", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(v.categorias))

        return 204, ""

    except FileNotFoundError:
        return 404, "arquivo não encontrado." 

def carregar_dados():
    try:
        with open("dados/itens.json", "r", encoding="utf-8") as arquivo:
            v.lista_itens = json.load(arquivo)

        with open("dados/pedidos.json", "r", encoding="utf-8") as arquivo:
            v.lista_pedidos = json.load(arquivo)

        with open("dados/info.json", "r", encoding="utf-8") as arquivo:
            v.info = json.load(arquivo)
        
        with open("dados/usuarios.json", "r", encoding="utf-8") as arquivo:
            v.usuarios = json.load(arquivo)

        with open("dados/categorias.txt", "r", encoding="utf-8") as arquivo:
            v.categorias = arquivo.read().splitlines()

        return 1
            
    except FileNotFoundError:
        return 0 

def autenticar(token):
    for t in v.tokens:
        if token == t:
            nome = v.tokens.get(token)
            for usuario in v.usuarios:
                if usuario["nome"] == nome:
                    return usuario
    return ""