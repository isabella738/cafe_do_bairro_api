from datetime import datetime, date
import random
import string
import json

# verificam formato da entrada 

def verificar_string(nome):
    if not isinstance(nome, str) or not nome.strip():
        return "conteudo invalido."
    
    return ""

def verificar_int(numero, a, b):
    if not isinstance(numero, int):
        return "conteudo invalido."
    
    if numero < a or numero > b:
        return "intervalo inválido"

    return ""

def verificar_valor(valor):
    if (erro := verificar_string(valor)) != "":
        return erro

    partes = valor.split(",")
    if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit() or len(partes[1]) != 2:
        return "formato monetario invalido."

    return ""

def verificar_telefone(telefone):
    if (erro := verificar_string(telefone)) != "":
        return erro
    
    if not telefone.isdigit() or len(telefone) != 11:
        return "formato de telefone invalido."
    
    return ""

def verificar_data(prazo):
    try:
        dia = datetime.strptime(prazo, "%Y-%m-%d").date()

        if horas_ate(prazo) <= 0:
            return "a data já passou."

    except (ValueError, TypeError):
        return "data invalida."
    
    return ""

def pertence(item, lista):
    if not item in lista:
        return "campo/item não pertence ao objeto."
    return ""

def verificar_pedido(codigos, lista_itens, lista_pedidos, data):
    if not isinstance(codigos, list) or len(codigos) <= 0:
        return "pedido vazio."

    itens = [retornar_item(codigo, lista_itens) for codigo in codigos]

    if any(item == -1 for item in itens):
        return "pedido contém itens inexistentes."

    if any(item["status"] == 0 for item in itens):
        return "pedido contém itens indisponíveis."
    
    return ""

# outros
def disponibilidade(data, codigos, lista_pedidos, lista_itens):
    if not isinstance(codigos, list) or len(codigos) <= 0:
        return "pedido vazio."

    itens = [retornar_item(codigo, lista_itens) for codigo in codigos]

    bolos = sum(1 for i in itens if i["categoria"] == "bolo")

    for pedido in lista_pedidos:
        if pedido["prazo"] == data:
            itens = [retornar_item(codigo, lista_itens) for codigo in pedido["itens"]]
            bolos += sum(1 for item in itens if item["categoria"] == "bolo")
    
    if bolos > 5:
        return "limite diário de encomendas alcançado para este dia."
    return ""

def horas_ate(data): # pressupõe-se que o formato já esteja verificado ao chegar aqui
    dia = datetime.strptime(data, "%Y-%m-%d").date()
    return (dia - date.today()).total_seconds()/3600

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
            if nome.endswith(".json"):
                json.dump(variavel, arquivo, ensure_ascii=False, indent=4)
            else:
                arquivo.write("\n".join(variavel))

    except FileNotFoundError:
        raise 

def carregar_dados(nome):
    try:
        with open("dados/" + nome, "r", encoding = "utf-8") as arquivo:
            if nome.endswith(".json"):
                variavel = json.load(arquivo)
            else:
                variavel = arquivo.read().splitlines()
            
            return variavel
    except FileNotFoundError:
        raise 