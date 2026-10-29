import json

def salvar_itens(itens):
    with open("cafe do bairro/dados/itens.json", "w", encoding="utf-8") as arquivo:
        json.dump(itens, arquivo, ensure_ascii=False, indent=4)

def salvar_pedidos(pedidos):
    with open("cafe do bairro/dados/pedidos.json", "w", encoding="utf-8") as arquivo:
        json.dump(pedidos, arquivo, ensure_ascii=False, indent=4)

def carregar_itens():
    with open("cafe do bairro/dados/itens.json", "r", encoding="utf-8") as arquivo:
        itens = json.load(arquivo)
    return itens

def carregar_pedidos():
    with open("cafe do bairro/dados/pedidos.json", "r", encoding="utf-8") as arquivo:
        pedidos = json.load(arquivo)
    return pedidos
