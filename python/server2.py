import socket as sk
import sys


class WSGIServer(object):

    address_family = sk.AF_INET
    socket_type = sk.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):

        self.listen_socket = listen_socket = sk.socket(
                self.address_family,
                self.socket_type
                )
        listen_socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        listen_socket.bind(server_address)

        listen_socket.listen(self.request_queue_size)

        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = sk.getfqdn(host)
        self.server_port = port

        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket

        while True:
            self.client_connection, client_address = listen_socket.accept()

            self.handle_one_request()

    def handle_one_request(self):
        req_data = self.client_connection.recv(1024).decode("utf-8")

        self.request_data = request_data = req_data

        print("".join("< {line}\n".format(line=line)
                for line in request_data.splitlines()
                ))

        self.parse_request(request_data)

        env = self.get_environ()

        result = self.application(env, self.start_response)

        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip("\r\n")
        request_line = request_line.split()

        self.request_method = request_line[0]
        self.path = request_line[1]
        self.request_version = request_line[2]

    def get_environ(self):
        env = {}

        env["wgsi.version"]        = (1, 0)
        env["wsgi.url_scheme"]     = "http"
        env["wsgi.input"]          = self.request_data
        env["wsgi.errors"]         = sys.stderr
        env["wsgi.multithread"]    = False
        env["wsgi.multiprocess"]   = False
        env["wsgi.run_once"]       = False

        env["REQUEST_METHOD"]      = self.request_method
        env["PATH_INFO"]           = self.path
        env["SERVER_NAME"]         = self.server_name
        env["SERVER_PORT"]         = str(self.server_port)
        return env

    def start_response(self, status, response_headers, exc_info=None):
        server_headers = [
                ("Date", "Tue, 31 Mar 2015 12:54:48 GMT"),
                ("Server", "WSGIServer 0.2"),
        ]
        self.headers_set = [status, response_headers + server_headers]

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = "HTTP/1.1 {status}\r\n".format(status=status)
            for header in response_headers:
                response += "{0}: {1}\r\n".format(*header)
            response += "\r\n"
            for data in result:
                response += data.decode("utf-8")
            print(str("".join(
                "> {line}\n".format(line=line)
                for line in response.splitlines()
                )))
            resp = bytes(response, "UTF-8")
            self.client_connection.sendall(resp)
        finally:
            self.client_connection.close()

SERVER_ADDRESS = (HOST, PORT) = "", 22222

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

# Here is the flask application: --------
from flask import Flask
app = Flask("app")

@app.route("/hello", methods=["GET", "POST"])
def hello_world():
    return "hello word!"
application = app
# -------------------------------------------

if __name__ == "__main__":
    httpd = make_server(SERVER_ADDRESS, application)
    print("WSGIServer: Serving HTTP on port {port} ... \n".format(port=PORT))
    httpd.serve_forever()


