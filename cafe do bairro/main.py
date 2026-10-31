from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import date
from functions import *
import json

lista_itens = []
lista_pedidos = []
categorias = []
info = {}
variaveis = [lista_itens, lista_pedidos, info, categorias]

class Servidor(BaseHTTPRequestHandler):

    def enviar(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()

        self.wfile.write(corpo)

    # listar
    def do_GET(self):
        url = urlparse(self.path)
        parametros = parse_qs(url.query)

        if url.path == "/encomendas":
            # exibe todas as encomendas, preferencialmente por ordem crescente de prazo, mas também
            # pode filtrar por alguma chave

            if not lista_pedidos:
                self.enviar(403, {"erro":"não existem pedidos."})
                return

            mensagens = []
            chave = parametros.get("chave", [None])[0]
            busca = parametros.get("busca", [None])[0]

            lista_pedidos.sort(key=lambda item: item["prazo"])

            # enviar todas as encomendas
            if chave == None:
                self.enviar(200, lista_pedidos)
                return
            
            # verificar entradas
            mensagens.append(verificar_string(busca))
            mensagens.append(pertence(chave, lista_pedidos[0]))

            # enviar erros
            erros = [m for m in mensagens if m != ""]
            if erros:
                self.enviar(400, {"erro":erros})
                return
            
            # caso especial: status (int)
            if chave == "status":
                try:
                    busca = int(busca)
                except ValueError:
                    self.enviar(400, {"erro":"status inválido."})
                    return
            
            # exibir com base em filtro
            lista = [p for p in lista_pedidos if p[chave] == busca]
            self.enviar(200, lista)

        elif url.path == "/cardapio":
            # lista os itens do cardápio na íntegra ou por categoria
            if not lista_itens:
                self.enviar(403, {"erro":"não existem itens."})
                return
                
            tipo = parametros.get("categoria", [None])[0]

            if tipo == None:
                self.enviar(200, lista_itens)
                return
            
            for categoria in categorias:
                if tipo == categoria:
                    lista = [i for i in lista_itens if i["categoria"] == categoria]
                    self.enviar(200, lista)
                    return
            
            self.enviar(404, {"erro":"categoria não encontrada"})
                        
        elif url.path == "/informacoes":
            self.enviar(200, info)

        elif url.path == "/produto":
            # como os itens de um pedido são armazenados como números, acho que isso pode ser útil.
            # isso devolve as informaçẽos de um item dado seu número/código

            codigo = parametros.get("codigo", [None])[0]

            if codigo == None:
                self.enviar(400, {"erro":"cliente não enviou parâmetro."})
                return

            item = retornar_item(codigo, lista_itens)
            if item != -1:
                self.enviar(200, item)
                return
            
            self.enviar(404, {"erro":"item não encontrado."})
                
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
                mensagens.append(verificar_string(nome))

                # numero de telefone
                telefone = dados.get("telefone")
                mensagens.append(verificar_telefone(telefone))

                # data de entrega
                prazo = dados.get("prazo")
                mensagens.append(verificar_data(prazo))

                # itens do pedido
                itens = dados.get("itens")
                mensagens.append(verificar_pedido(itens, lista_itens, lista_pedidos, prazo))

                # observações sobre o pedido, se houver
                comentario = dados.get("comentario")

                #envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return
                
                if (erro := disponibilidade(prazo, itens, lista_pedidos, lista_itens)):
                    self.enviar(403, {"erro":erro})
                    return

                # montar pedido
                pedido = {
                    "nome": nome,
                    "telefone": telefone,
                    "prazo": prazo,
                    "itens": itens,
                    "comentario": comentario,
                    "status": 0,
                    "codigo": gerar_codigo(lista_pedidos)
                }

                lista_pedidos.append(pedido)
                
                self.enviar(201, pedido)

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/criar_item":

            try:
                dados = json.loads(corpo)
                mensagens = []

                # nome do produto
                nome = dados.get("nome")
                mensagens.append(verificar_string(nome))

                # valor do produto
                valor = dados.get("valor")
                mensagens.append(verificar_valor(valor))

                # categoria do produto
                categoria = dados.get("categoria")
                mensagens.append(pertence(categoria, categorias))

                # envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return
                
                # montar o item
                item = {
                    "nome": nome,
                    "categoria": categoria,
                    "valor": valor,
                    "status": 1,
                    "codigo": gerar_codigo(lista_itens)
                }

                lista_itens.append(item)

                self.enviar(201, item)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})
        
        elif self.path == "/criar_categoria":

            try:
                dados = json.loads(corpo)
                novo = dados["categoria"]

                if (erro := verificar_string(novo)):
                    self.enviar(400, {"erro":erro})
                    return

                if novo in categorias:
                    self.enviar(400, {"erro":"categoria já existe."})
                    return

                categorias.append(novo)
                self.enviar(200, novo)
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # modificar/atualizar
    def do_PATCH(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/atualizar_status":
            if not lista_pedidos:
                self.enviar(403, {"erro":"não existem pedidos."})
                return

            try:
                dados = json.loads(corpo)
                mensagens = []
                
                codigo = dados["codigo"]
                mensagens.append(verificar_string(codigo))

                novo_status = dados["status"]
                mensagens.append(verificar_int(novo_status, 0, 3))

                #envio de erros
                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return

                for pedido in lista_pedidos:
                    if codigo == pedido["codigo"]:
                        pedido["status"] = novo_status
                        self.enviar(204, "")
                        return
                
                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})
        
        elif self.path == "/editar_pedido":
            if not lista_pedidos:
                self.enviar(403, {"erro":"não existem pedidos."})
                return
                
            try:
                dados = json.loads(corpo)
                mensagens = []

                # leitura de dados
                codigo = dados["codigo"]
                mensagens.append(verificar_string(codigo))

                novo = dados["novo_conteudo"]

                chave = dados["chave"] 
                mensagens.append(pertence(chave, lista_pedidos[0]))      

                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return

                # modificação do pedido
                for pedido in lista_pedidos:
                    if codigo == pedido["codigo"]:

                        if horas_ate(pedido["prazo"]) <= 24:
                            self.enviar(403, {"erro":"modificações só podem ser feitas até 24 horas antes da retirada."})
                            return

                        match chave:
                            case "telefone":
                                mensagens.append(verificar_telefone(novo))
                            case "nome":
                                mensagens.append(verificar_string(novo))
                            case "prazo":
                                mensagens.append(verificar_data(novo))
                                mensagens.append(disponibilidade(novo, pedido["itens"], lista_pedidos, lista_itens))
                            case "itens":
                                mensagens.append(verificar_pedido(novo, lista_itens, lista_pedidos, pedido["prazo"]))
                            case "comentario":
                                pass
                            case _:
                                self.enviar(403, {"erro":"essa chave não é editável."})
                                return

                        #envio de erros
                        erros = [m for m in mensagens if m != ""]
                        if erros:
                            self.enviar(400, {"erro":erros})
                            return
                        
                        if chave == "itens" and (erro := disponibilidade(pedido["prazo"], novo, lista_pedidos, lista_itens)):
                            self.enviar (403, {"erro":erro})
                        
                        # conclusão
                        pedido[chave] = novo
                        self.enviar(204, "")
                        return

                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/editar_produto":
            if not lista_itens:
                self.enviar(403, {"erro":"não existem itens."})
                return
                
            try:
                dados = json.loads(corpo)
                mensagens = []

                # ler dados
                codigo = dados["codigo"]
                mensagens.append(verificar_string(codigo))

                novo = dados["novo_conteudo"]

                chave = dados["chave"] # nome da chave a ser modificada
                mensagens.append(pertence(chave, lista_itens[0]))     

                erros = [m for m in mensagens if m != ""]
                if erros:
                    self.enviar(400, {"erro":erros})
                    return

                # modificação do item
                for item in lista_itens:
                    if codigo == item["codigo"]:

                        match chave:
                            case "valor":
                                mensagens.append(verificar_valor(novo))
                            case "nome":
                                mensagens.append(verificar_string(novo))
                            case "categoria":
                                mensagens.append(pertence(novo, categorias))
                            case "status":
                                mensagens.append(verificar_int(novo, 0, 1))
                            case _:
                                self.enviar(404, {"erro":"chave inexistente ou invalida."})
                                return

                        #envio de erros
                        erros = [m for m in mensagens if m != ""]
                        if erros:
                            self.enviar(400, {"erro":erros})
                            return
                        
                        item[chave] = novo
                        self.enviar(204, "")
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
                self.enviar(204, "")
                return

                self.enviar(404, {"erro": "item não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/carregar_dados":
            try:
                nomes = ["itens.json", "pedidos.json", "info.json", "categorias.txt"]
                
                contador = 0
                for i in range(4):
                    dados = carregar_dados(nomes[i])
                    
                    if isinstance(variaveis[i], dict):
                        variaveis[i].clear()
                        variaveis[i].update(dados)
                    else:
                        variaveis[i][:] = dados

                    contador += len(variaveis[i])

                self.enviar(200, variaveis)
            
            except FileNotFoundError:
                self.enviar(404, {"erro":"arquivo não encontrado."})

        elif self.path == "/salvar_dados":
            try:
                nomes = ["itens.json", "pedidos.json", "info.json", "categorias.txt"]
                
                for i in range(4):
                    salvar_dados(nomes[i], variaveis[i])
                self.enviar(204, "")
            
            except FileNotFoundError:
                self.enviar(404, {"erro":"arquivo não encontrado."})

        else:
            self.enviar(404, {"erro":"não encontrado."})

    # exluir
    def do_DELETE(self):
        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam)

        if self.path == "/excluir_pedido": 
            # para concluir ou recusar um pedido

            if not lista_pedidos:
                self.enviar(403, {"erro":"não existem pedidos."})
                return
                
            try:
                dados = json.loads(corpo)
                codigo = dados["codigo"]
                if (erro := verificar_string(codigo)):
                    self.enviar(400, {"erro":erro})
                    return
                
                for pedido in lista_pedidos:
                    if codigo == pedido["codigo"]:
                        lista_pedidos.remove(pedido)
                        self.enviar(204, "")
                        return

                self.enviar(404, {"erro":"não encontrado."})
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/cancelar_pedido": 
            # para um cliente cancelar um pedido

            if not lista_pedidos:
                self.enviar(403, {"erro":"não existem pedidos."})
                return
                
            try:
                dados = json.loads(corpo)
                codigo = dados["codigo"]
                if (erro := verificar_string(codigo)):
                    self.enviar(400, {"erro":erro})
                    return

                for pedido in lista_pedidos:
                    if codigo == pedido["codigo"]:

                        if horas_ate(pedido["prazo"]) <= 24:
                            self.enviar(403, {"erro":"modificações só podem ser feitas até 24 horas antes da retirada."})
                            return

                        lista_pedidos.remove(pedido)
                        self.enviar(204, "")
                        return
                
                self.enviar(404, {"erro": "pedido não encontrado."})

            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/excluir_item":
            # itens não podem ser excluídos se estiverem em algum pedido existente.
            # é preciso antes recusá-lo ou concluí-lo nesse caso

            if not lista_itens:
                self.enviar(403, {"erro":"não existem itens."})
                return
                
            try:
                dados = json.loads(corpo)

                codigo = dados["codigo"]
                if (erro := verificar_string(codigo)):
                    self.enviar(400, {"erro":erro})
                    return

                produto = retornar_item(codigo, lista_itens)
                if produto == -1:
                    self.enviar(404, {"erro":"item não encontrado."})
                    return

                for pedido in lista_pedidos:
                    if any(codigo == i for i in pedido["itens"]):
                        self.enviar(403, {"erro":"existe pedido ativo com este item."})
                        return

                lista_itens.remove(produto)
                self.enviar(204, "")
                return


            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        elif self.path == "/excluir_categoria":
            # itens da categoria excluída vão para 'outros'

            try:
                dados = json.loads(corpo)
                categoria = dados["categoria"]

                if (erro := verificar_string(categoria)):
                    self.enviar(400, {"erro":erro})
                    return

                if not categoria in categorias:
                    self.enviar(404, {"erro":"categoria não encontrada"})
                    return
                
                if categoria == "outros":
                    self.enviar(403, {"erro":"esta categoria não é editável."})

                for item in lista_itens:
                    if item["categoria"] == categoria:
                        item["categoria"] = "outros"
                
                categorias.remove(categoria)
                self.enviar(204, "")
                
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.enviar(400, {"erro": "JSON inválido"})

        else:
            self.enviar(404, {"erro":"não encontrado."})

if __name__ == "__main__":
    servidor = HTTPServer(("localhost", 8000), Servidor)

    print("Servidor iniciado em http://localhost:8000")

    servidor.serve_forever()