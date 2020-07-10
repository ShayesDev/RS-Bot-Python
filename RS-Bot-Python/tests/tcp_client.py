import socket
import time

server_ip = '192.168.254.71'     # or 127.0.0.1
server_port = 58000
server_addr = (server_ip, server_port)

buffer_size = 1024

while True:
    try:
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockobj.connect(server_addr)
        message = input('TCP Client> ')
        num = sockobj.sendall(message.encode())
        if not message:
            break
        
    finally:    
        sockobj.close()
