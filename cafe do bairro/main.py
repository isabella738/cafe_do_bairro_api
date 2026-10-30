from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from functions import *
from save import *

lista_itens = carregar_itens()
lista_pedidos = carregar_pedidos()
categorias = carregar_categorias()
info = carregar_informacoes()    

class Servidor(BaseHTTPRequestHandler):

    def enviar(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()

        self.wfile.write(corpo)

    # visualizar
    def do_GET(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/encomendas":
            try:
                dados = json.loads(corpo)
                chave = dados["chave"]
                busca = dados["busca"]

                # ver todas as encomendas
                if chave == 0:
                    lista_pedidos.sort(key=lambda item: item["prazo"])
                    self.enviar(200, lista_pedidos)
                    return
                
                if not chave in pedido:
                    self.enviar(404, {"erro":"não encontrado."})
                    return
                
                # exibir com base em filtro
                lista = [p for p in total_pedidos if p[chave] == busca]
                self.enviar(200, lista)

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/cardapio":

            try:
                dados = json.loads(corpo)
                tipo = dados["categoria"]

                if categoria == 0:
                    self.enviar(200, lista_itens)
                    return
                
                for categoria in categorias:
                    if tipo == categoria:
                        lista = [i for i in lista_itens if i["categoria"] == categoria]
                        self.enviar(200, lista)
                        return
                
                self.enviar(404, {"erro":"categoria não encontrada"})
                        
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/informações":
            self.enviar(200, info)

        elif self.path == "/produto":
            try:
                dados = json.loads(corpo)
                numero = dados["numero"]

                item = retornar_item(numero, lista_itens)
                if item != -1:
                    self.enviar(200, item)
                    return
                
                self.enviar(404, {"erro":"item não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # criar
    def do_POST(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/criar_pedido":

            try:
                dados = json.loads(corpo)
                mensagens = []

                # nome do cliente
                nome = dados.get("nome")
                if not isinstance(nome, str) or not nome.strip():
                    mensagens.append("nome do cliente não pode ser vazio.")

                # numero de telefone
                telefone = dados.get("telefone")
                mensagens.append(verificar_telefone(telefone))

                # data de entrega
                prazo = dados.get("prazo")
                mensagens.append(verificar_data(prazo, lista_pedidos))

                # itens do pedido
                itens = dados.get("itens")
                mensagens.append(verificar_pedido(itens, lista_itens))

                # observações sobre o pedido, se houver
                comentario = dados.get("comentario")

                #envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return

                # montar pedido
                pedido = {
                    "nome": nome,
                    "telefone": telefone,
                    "prazo": prazo,
                    "itens": itens,
                    "comentario": comentario,
                    "status": 0,
                    "codigo": criar_codigo(lista_pedidos)
                }

                lista_pedidos.append(pedido)
                salvar_pedidos(lista_pedidos)
                
                self.enviar(201, pedido)

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/criar_item":

            try:
                dados = json.loads(corpo)
                mensagens = []

                # nome do produto
                nome = dados.get("nome")
                mensagens.append(verificar_nome_produto(nome, lista_itens))

                # valor do produto
                valor = dados.get("valor")
                mensagens.append(verificar_valor(valor))

                # categoria do produto
                categoria = dados.categoria("categoria")
                if not categoria in categorias:
                    mensagens.append("categoria não encontrada.")

                #envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return
                
                # montar o item
                item = {
                    "nome": nome,
                    "valor": valor,
                    "categoria": categoria,
                    "numero": lista_itens.top()["numero"] + 1,
                    "status": 1
                }

                lista_itens.append(item)
                salvar_itens(lista_itens)

                self.enviar(201, item)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})
        
        elif self.path == "/criar_categoria":

            try:
                dados = json.loads(corpo)
                novo = dados["categoria"]

                if categoria in categorias:
                    self.enviar(400, {"erro":"categoria já existe."})
                    return

                categorias.append(novo)
                salvar_categorias(categorias)
                self.enviar(200, categoria)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # modificar informação
    def do_PATCH(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/modificar_status":

            try:
                dados = json.loads(corpo)
                
                encomenda = dados["pedido"]
                novo_status = dados["status"]

                for pedido in lista_pedidos:
                    if encomenda["codigo"] == pedido["codigo"]:
                        pedido["status"] = novo_status
                        salvar_pedidos(lista_pedidos)
                        self.enviar(204, "")
                        return
                
                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})
        
        elif self.path == "/editar_pedido":

            try:
                dados = json.loads(corpo)
                mensagens = []

                encomenda = dados["encomenda"]
                novo = dados["novo_conteudo"]
                chave = dados["chave"] # nome da chave a ser modificada                    

                for pedido in lista_pedidos:
                    if encomenda["codigo"] == pedido["codigo"]:

                        diferenca = date.today() - pedido["prazo"]
                        if diferenca.total_seconds()/3600 <= 24:
                            self.enviar(403, {"erro":"modificações só podem ser feitas até 24 horas antes da retirada."})
                            return

                        match chave:
                            case "telefone":
                                mensagens.append(verificar_telefone(novo))
                            case "prazo":
                                mensagens.append(verificar_data(novo, lista_pedidos))
                            case "itens":
                                mensagens.append(verificar_pedido(novo, lista_itens))
                            case "comentario":
                                pass
                            case "nome":
                                if not isinstance(novo, str) or not novo.strip():
                                    mensagens.append("nome do cliente não pode ser vazio.")
                            case _:
                                self.enviar(404, {"erro":"chave inexistente ou invalida."})
                                return

                        #envio de erros
                        erros = [m for m in mensagens if m != ""]
                        if erros:
                            self.enviar(400, {"erro":erros})
                            return
                        
                        pedido[chave] = novo
                        salvar_pedidos(lista_pedidos)
                        self.enviar(204,{"status":"modificação bem sucedida"})
                        return

                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/editar_produto":

            try:
                dados = json.loads(corpo)
                mensagens = []

                produto = dados["item"]
                novo = dados["novo_conteudo"]
                chave = dados["chave"] # nome da chave a ser modificada                    

                for item in lista_itens:
                    if produto["codigo"] == item["codigo"]:

                        match chave:
                            case "valor":
                                mensagens.append(verificar_valor(novo))
                            case "nome":
                                mensagens.append(verificar_nome_produto(novo, lista_itens))
                            case "categoria":
                                if not novo in categorias:
                                    mensagens.append("categoria invalida.")
                            case "status":
                                if novo != 0 and novo != 1:
                                    mensagens.append("status inválido.")
                            case _:
                                self.enviar(404, {"erro":"chave inexistente ou invalida."})
                                return

                        #envio de erros
                        erros = [m for m in mensagens if m != ""]
                        if erros:
                            self.enviar(400, {"erro":erros})
                            return
                        
                        item[chave] = novo
                        salvar_itens(lista_itens)
                        self.enviar(204,{"status":"modificação bem sucedida"})
                        return

                self.enviar(404, {"erro": "item não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/editar_informacoes":
            try:
                dados = json.loads(corpo)

                novo = dados["novo_conteudo"]
                chave = dados["chave"]            

                if not chave in info:
                    self.enviar(404, {"erro":"não encontrado"})
                    return
                
                info[chave] = novo
                salvar_informacoes(info)
                self.enviar(204,{"status":"modificação bem sucedida"})
                return

                self.enviar(404, {"erro": "item não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # exluir
    def do_DELETE(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/recusar_pedido":
            # enviar mensagem do corpo por sms
            # a ideia é que a requisição envie traga uma mensagem de justificativa para o cliente
            try:
                dados = json.loads(corpo)
                encomenda = dados["pedido"]
                
                for pedido in lista_pedidos:
                    if encomenda == pedido:
                        lista_pedidos.remove(pedido)
                        self.enviar(204, {"status":"bem-sucedido"})
                        return
                self.enviar(404, {"erro":"não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/concluir_pedido":
            # depois que o pedido já foi entregue
            try:
                dados = json.loads(corpo)
                encomenda = dados["pedido"]
                
                for pedido in lista_pedidos:
                    if encomenda == pedido:
                        lista_pedidos.remove(pedido)
                        self.enviar(204, {"status":"bem-sucedido"})
                        return
                self.enviar(404, {"erro":"não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/cancelar_pedido":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

            try:
                dados = json.loads(corpo)
                encomenda = dados["encomenda"]

                for pedido in lista_pedidos:
                    if encomenda["codigo"] == pedido["codigo"]:

                        diferenca = date.today() - pedido["prazo"]
                        if diferenca.total_seconds()/3600 <= 24:
                            self.enviar(403, {"erro":"modificações só podem ser feitas até 24 horas antes da retirada."})
                            return

                        lista_pedidos.remove(pedido)
                        self.enviar(204, {"status":"bem-sucedido"})
                
                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/excluir_item":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

            try:
                dados = json.loads(corpo)
                numero = dados["item"]
                produto = retornar_item(numero, lista_itens)

                for item in itens:
                    if item["nome"] == produto["nome"]:
                        
                        for pedido in lista_pedidos:
                            if any(numero == i for i in pedido["itens"]):
                                self.enviar(403, {"erro":"existe pedido ativo com este item."})
                                return
                        
                        lista_itens.remove(item)
                        self.enviar(204, {"status":"bem-sucedido."})
                        return

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/excluir_categoria":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

            try:
                dados = json.loads(corpo)
                categoria = dados["categoria"]

                for item in lista_itens:
                    if item["categoria"] == categoria:
                        item["categoria"] = "outros"
                
                categorias.remove(categoria)
                self.enviar(204)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})
