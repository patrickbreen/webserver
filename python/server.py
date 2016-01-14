from socket import *

HOST, PORT = "", 22222


listen_socket = socket(AF_INET, SOCK_STREAM)
listen_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print("Serving HTTP on localhost, port %s ..." % PORT)

while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print(request)

    http_response = """HTTP/1.1 200 OK

    Hello, World!
    """
    http_response = bytes(http_response, 'UTF-8')
    client_connection.sendall(http_response)
    client_connection.close()
