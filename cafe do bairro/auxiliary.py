# Funções de auxílio às principais em functions.py

from datetime import datetime, date
import variables as v
import random
import string

# Auxiliares
def disponibilidade(data, codigos, ignorar):
    # pressupõe-se que os itens em "codigos" já foram validados antes da chamada desta
    # função

    if not isinstance(codigos, list) or len(codigos) <= 0:
        return "pedido vazio."

    itens = [retornar_item(codigo, v.lista_itens) for codigo in codigos]

    bolos = sum(1 for i in itens if i["categoria"] == "bolo")

    for pedido in v.lista_pedidos:
        if pedido == ignorar:
            pass
        if pedido["prazo"] == data:
            itens = [retornar_item(codigo, v.lista_itens) for codigo in pedido["itens"]]
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

# Validação
def verificar_string(nome):
    # verifica se é string e não vazia

    if not isinstance(nome, str) or not nome.strip():
        return "falta conteúdo ou conteudo invalido."
    
    return ""

def verificar_int(numero, a, b):
    # verifica se é um inteiro no intervalo [a, b]

    if  not isinstance(numero, int):
        return "falta conteúdo ou conteudo invalido."
    
    if numero < a or numero > b:
        return "intervalo inválido"

    return ""

def verificar_valor(valor):
    # verifica o formato monetário com vírgula e duas casas decimais

    if (erro := verificar_string(valor)) != "":
        return erro

    partes = valor.split(",")
    if len(partes) != 2 or not partes[0].isdigit() or not partes[1].isdigit() or len(partes[1]) != 2:
        return "formato monetario invalido."

    return ""

def verificar_telefone(telefone):
    # verifica o formato do tipo 73900000000 (11 dígitos)

    if (erro := verificar_string(telefone)) != "":
        return erro
    
    if not telefone.isdigit() or len(telefone) != 11:
        return "formato de telefone invalido."
    
    return ""

def verificar_data(prazo):
    # verifica o formato e se a data já não passou. a verificação da disponibilidade
    # do dia é feita depois.

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

def verificar_pedido(codigos, lista_itens):
    # só verifica se os itens da lista 'codigos' existem. a verificação da disponibilidade
    # do dia é feita depois.

    if not isinstance(codigos, list) or len(codigos) <= 0:
        return "pedido vazio."

    itens = [retornar_item(codigo, lista_itens) for codigo in codigos]

    if any(item == -1 for item in itens):
        return "pedido contém itens inexistentes."

    if any(item["status"] == 0 for item in itens):
        return "pedido contém itens indisponíveis."
    
    return ""
