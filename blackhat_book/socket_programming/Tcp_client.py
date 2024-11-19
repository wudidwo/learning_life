import socket

target_host="127.0.0.1"
target_port=9999

#t_address=[target_host,target_port]

client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)#创建了一个基于IPv4的TCP套接字
client.connect((target_host,target_port))
try:
    http_request='123465789'
    client.send(http_request.encode('utf-8'))
except Exception as e:
    print(e)
else:
    response=client.recv(4096)
    print(response)
finally:
    client.close()

