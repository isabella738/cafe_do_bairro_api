# Onde o servidor é iniciado

from http.server import HTTPServer, BaseHTTPRequestHandler
from save import carregar_dados, salvar_dados, autenticar
from endpoints import direcionar_requisicao
import json
import sys

if not carregar_dados():
    print("Arquivo não encontrado. Não foi possível carregar os dados.")
    sys.exit(0)

class Servidor(BaseHTTPRequestHandler):

    def do_GET(self):
        self.processar()

    def do_POST(self):
        self.processar()

    def do_PATCH(self):
        self.processar()

    def do_DELETE(self):
        self.processar()

    def processar(self):
        token = self.headers.get("Authorization")
        usuario = None

        if token:
            token = token.replace("Bearer ", "")
            usuario = autenticar(token)

        tam = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tam).decode("utf-8") if tam else ""

        try:
            dados = json.loads(corpo) if corpo else None
        except json.JSONDecodeError:
            self.enviar(400, {"erro": "JSON inválido."})
            return
    
        codigo, retorno = direcionar_requisicao(self.command, self.path, dados, usuario, token)
        salvar_dados()
        self.enviar(codigo, retorno)

    def enviar(self, codigo, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")

        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()

        self.wfile.write(corpo)

if __name__ == "__main__":
    servidor = HTTPServer(("0.0.0.0", 8000), Servidor)

    print("Servidor iniciado em http://localhost:8000")

    servidor.serve_forever()