import socket,threading

s_address=('0.0.0.0',9999)

Tcp_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

Tcp_server.bind(s_address)

Tcp_server.listen(5)#启动监听并设置最大连接数为5
print("[*] listen on %s:%d" % (s_address[0],s_address[1]))

def handle_client(client):
    response=client.recv(4096) #接收客户端的信息

    print("[*] received : %s" % response)

    message='ACK'
    client.send(message.encode('utf-8')) #byte


while True:
    client,addr=Tcp_server.accept()

    print("[*] Accept connect from %s:%d" % (addr[0],addr[1]))

    client_handler=threading.Thread(target=handle_client,args=(client,))

    client_handler.start()