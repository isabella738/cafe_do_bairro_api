from datetime import datetime
import random
import string

def bolos_no_dia(data, lista):
    bolos = 0
    for pedido in lista:
        if pedido["prazo"] == data:
            bolos += sum(1 for item in pedido["itens"] if item["tipo"] == "bolo")

    return bolos

def item_duplicado(nome, lista):
    for item in lista:
        if nome == lista["nome"]:
            return 1
    return 0

def valor_total(itens):
    total = 0.0
    for item in itens:
        total += float(item["valor"].replace(",", "."))
    return total

def verificar_valor(valor):
    if not isinstance(valor, str) or not valor.strip():
        return "conteudo invalido."

    partes = valor.split(",")
    if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit or len(partes[1]) != 2:
        return "formato monetario invalido."

    return ""

def verificar_nome_produto(item, lista):
    if not isinstance(item, str) or not item.strip():
        return "conteudo invalido."
    
    if item_duplicado(item, lista):
        return "ja existe produto com este nome."
    
    return ""

def verificar_telefone(telefone):
    if not isinstance(telefone, str) or not telefone.strip():
        return "conteudo invalido."
    
    if not telefone.isdigit() or len(telefone) != 11
        return "formato de telefone invalido."
    
    return ""

def verificar_data(prazo, lista):
    data = 0
    try:
        data = datetime.strptime(prazo, "%Y-%m-%d").date()

        if data <= date.today():
            return "o pedido deve ser feito com 24 horas de antecedência."

    except (ValueError, TypeError):
        return "data invalida."
    
    if bolos_no_dia(prazo, lista) >= 5:
        return "maximo alcançado de encomendas feitas para este dia."
    
    return ""

def verificar_pedido(itens, lista, data):
    if len(itens) <= 0:
        return "pedido vazio."

    for item in itens:
        if not any(item["nome"] == produto["nome"] for produto in lista):
            return "um ou mais produtos não existem no cardápio."
        
    bolos = sum(1 for item in itens if item["tipo"] == "bolo")
    if bolos + bolos_no_dia(data, lista) >= 5:
        return "o pedido estoura o máximo permitido de encomendas feitas para este dia."
    
    return ""

def criar_codigo(lista):
    caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
    
    while True:
        codigo = "".join(random.choices(caracteres, k=5))

        if not any(codigo == pedido["codigo"] for pedido in lista)
            return codigo
