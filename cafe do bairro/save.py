import json

def salvar_itens(itens):
    try:
        with open("cafe do bairro/dados/itens.json", "w", encoding="utf-8") as arquivo:
            json.dump(itens, arquivo, ensure_ascii=False, indent=4)
    except:
        return []

def salvar_pedidos(pedidos):
    try:
        with open("cafe do bairro/dados/pedidos.json", "w", encoding="utf-8") as arquivo:
            json.dump(pedidos, arquivo, ensure_ascii=False, indent=4)
    except:
        return []

def salvar_categorias(categorias):
    try:
        with open("cafe do bairro/dados/categorias.txt", "w", encoding="utf-8") as arquivo:
            arquivo.write(categorias)
    except:
        return []

def salvar_informacoes(informacoes):
    try:
        with open("cafe do bairro/dados/info.json", "w", encoding="utf-8") as arquivo:
            json.dump(informacoes, arquivo, ensure_ascii=False, indent=4)
    except:
        return []

def carregar_itens():
    try:
        with open("cafe do bairro/dados/itens.json", "r", encoding="utf-8") as arquivo:
            itens = json.load(arquivo)
        return itens
    except:
        return []

def carregar_pedidos():
    try:
        with open("cafe do bairro/dados/pedidos.json", "r", encoding="utf-8") as arquivo:
            pedidos = json.load(arquivo)
        return pedidos
    except:
        return []

def carregar_categorias():
    try:
        with open("cafe do bairro/dados/categorias.txt", "r", encoding="utf-8") as arquivo:
            categorias = arquivo.readlines()
        return categorias
    except:
        return []

def carregar_informacoes():
    try:
        with open("cafe do bairro/dados/info.json", "r", encoding="utf-8") as arquivo:
            info = json.load(arquivo)
        return info
    except:
        return []