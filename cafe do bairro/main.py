from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from functions import valor_valido, item_duplicado
from salvar import carregar_itens, carregar_pedidos
from datetime import datetime

lista_itens = carregar_itens()
lista_pedidos = carregar_pedidos()
lista_usuarios = carregar_usuarios()

total_itens = len(lista_itens)
total_pedidos = len(lista_pedidos)


class Servidor(BaseHTTPRequestHandler):
    # visualizar
    def do_GET(self):
        if self.path == "/encomendas":
            lista_pedidos.sort(key=lambda item: item["prazo"])
            self.enviar(200, lista_pedidos)

        elif self.path == "/cardapio":
            self.enviar(200, lista_itens)

        elif self.path == "/meus_pedidos":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)
            
            try:
                dados = json.loads(corpo)
                codigo = dados["codigo"]

                for pedido in lista_pedidos:
                    if codigo == pedido["codigo"]:
                        self.enviar(200, pedido)
                        return

                self.enviar(404, {"erro":"pedido nao encontrado."})
            
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # criar
    def do_POST(self):
        if self.path == "/criar_pedido":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

            try:
                global lista_pedidos
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

                pedido = {
                    "nome": nome,
                    "telefone": telefone,
                    "prazo": prazo,
                    "itens": itens,
                    "comentario": comentario,
                    'valor_total': valor_total(itens),
                    "status": 0,
                    "codigo": criar_codigo(lista_pedidos)
                }

                lista_pedidos.append(pedido)
                salvar_pedidos(lista_pedidos)
                
                self.enviar(201, pedido)

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/criar_item":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

            try:
                global lista_itens
                dados = json.loads(corpo)
                mensagens = []

                # nome do produto
                nome = dados.get("nome")
                mensagens.append(verificar_nome_produto(nome, lista_itens))

                # valor do produto
                valor = dados.get("valor")
                mensagens.append(verificar_valor(valor))

                

                #envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return
                
                item = {
                    "nome": nome,
                    "valor": valor
                    "tipo":
                    "status": 1
                }

                lista_itens.append(item)
                salvar_itens(lista_itens)

                self.enviar(201, item)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})
        
        else:
            self.enviar(404, {"erro":"não encontrado."})

    # modificar informação de uma encomenda
    def do_PATCH(self):
        if self.path == "/modificar_status":
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

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
            tam = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tam)

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

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # exluir
    def do_DELETE(self):
        if self.path == "/recusar_pedido":
            # enviar mensagem do corpo por sms

        elif self.path == "/concluir_pedido":
            # depois que o pedido já foi entregue

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
                global lista_itens, lista_pedidos
                dados = json.loads(corpo)
                produto = dados["item"]

                for item in itens:
                    if item["nome"] == produto["nome"]:
                        
                        for pedido in lista_pedidos:
                            if item == i for i in pedido["itens"]
                                self.enviar(, {"erro":"existe pedido ativo com este item."})
                                return
                        
                        lista_itens.remove(item)
                        self.enviar(204, {"status":"bem-sucedido."})
                        return

        else:
            self.enviar(404, {"erro":"não encontrado."})

    def enviar(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()

        self.wfile.write(corpo)

