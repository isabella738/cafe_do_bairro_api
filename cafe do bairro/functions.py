from datetime import datetime, date
import random
import string
import json
import os

# verificam formato de entrada e outras coisas
def verificar_valor(valor):
    if not isinstance(valor, str) or not valor.strip():
        return "conteudo invalido."

    partes = valor.split(",")
    if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit or len(partes[1]) != 2:
        return "formato monetario invalido."

    return ""

def verificar_nome_produto(nome, lista):
    if not isinstance(nome, str) or not nome.strip():
        return "conteudo invalido."
    
    if item_duplicado(nome, lista):
        return "ja existe produto com este nome."
    
    return ""

def verificar_telefone(telefone):
    if not isinstance(telefone, str) or not telefone.strip():
        return "conteudo invalido."
    
    if not telefone.isdigit() or len(telefone) != 11:
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

def verificar_pedido(codigos, lista_itens, lista_pedidos, data):
    itens = [retornar_item(codigo, lista_itens) for codigo in codigos]

    if len(itens) <= 0:
        return "pedido vazio."

    for item in itens:
        if not any(item["nome"] == produto["nome"] for produto in lista_itens):
            return "um ou mais produtos não existem no cardápio."
        if item["status"] == 0:
            return "item temporariamente indisponível."

    bolos = sum(1 for item in itens if item["categoria"] == "bolo")
    if bolos + bolos_no_dia(data, lista_pedidos) >= 5:
        return "o pedido estoura o máximo permitido de encomendas feitas para este dia."
    
    return ""

# outros
def bolos_no_dia(data, lista):
    bolos = 0
    for pedido in lista:
        if pedido["prazo"] == data:
            bolos += sum(1 for item in pedido["itens"] if item["categoria"] == "bolo")

    return bolos

def item_duplicado(nome, lista):
    if any(item["nome"] == nome for item in lista):
        return 1
    return 0

def gerar_codigo(lista):
    caracteres = string.ascii_uppercase + string.ascii_lowercase + string.digits
    
    while True:
        codigo = "".join(random.choices(caracteres, k=5))

        if not any(codigo == pedido["codigo"] for pedido in lista):
            return codigo

def retornar_item(codigo, lista):
    for item in lista:
        if item["codigo"] == codigo:
            return item
    return -1

# carregamento e salvamento de dados
def salvar_dados(nome, variavel):
    try:
        with open("dados/" + nome, "w", encoding="utf-8") as arquivo:
            ponto = nome.find(".")
            if nome[ponto + 1:] == "json":
                json.dump(variavel, arquivo, ensure_ascii=False, indent=4)
            else:
                arquivo.write("\n".join(variavel))

    except FileNotFoundError:
        raise 

def carregar_dados(nome):
    try:
        with open("dados/" + nome, "r", encoding = "utf-8") as arquivo:
            ponto = nome.find(".")
            if nome[ponto + 1:] == "json":
                variavel = json.load(arquivo)
            else:
                variavel = arquivo.read().splitlines()
            
            return variavel
    except FileNotFoundError:
        print(f"dados/{nome}")
        print("Diretório atual:", os.getcwd())
        raise 