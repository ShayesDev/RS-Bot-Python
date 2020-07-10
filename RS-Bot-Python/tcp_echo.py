import socket
import bot

def main():
    my_ip = ''
    my_port = 50008
    my_addr = (my_ip, my_port)
    buffer_length = 1024

    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj.bind(my_addr)
    sockobj.listen()           # accept connections on this socket
    
    try:
        while True:
            connection,client_addr = sockobj.accept()
            
            try:
                data = connection.recv(buffer_length)
                if data:
                    bot.handle_api(data,connection)

            finally:
                connection.close()

    finally:
        sockobj.close()
        
