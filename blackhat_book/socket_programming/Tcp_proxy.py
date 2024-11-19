import sys
import socket
import threading
import argparse


def response_handler(buffer):
    #接收远程主机的数据包的处理，加代码处理
    return buffer


def request_handler(buffer):
    #对向远程主机请求数据包的处理，加代码处理
    return buffer

#十六进制转储函数
def hexdump(src,length=16):
    result=[]
    digits=4 if isinstance(src,str) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X".encode() % (digits, ord(x)) for x in s])
        text = b''.join([x.encode() if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))

    print(b'\n'.join(result))

def receive_from(remote_socket):
    remote_buffer=""
    remote_socket.settimeout(2)

    try:
        while True:
            data=remote_socket.recv(4096)
            remote_buffer+=data
            if not data:
                break
    except:
        pass

    return remote_buffer

def server_loop(local_host,local_port,remote_host,remote_port,recvive_first):
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        server.bind((local_host,local_port))
    except:
        print('Failed to listen on %s:%d' % (local_host,local_port))
        sys.exit()

    print("[*]listening on {0}:{1}".format(local_host,local_port))

    server.listen(5)

    while True:
        client_socket,addr=server.accept()
        print('[==>] Received incoming connetction froom %s:%d' % (addr[0],addr[1]))
        server_thread=threading.Thread(target=client_handler,args=(client_socket,remote_host,remote_port,recvive_first))
        server_thread.start()


def client_handler(client_socket,remote_host,remote_port,recvive_first):
    remote_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    #如果必要从远程主机接收数据
    if recvive_first:
        remote_buffer=receive_from(remote_socket)
        hexdump(remote_buffer)

        #发送到我们的响应处理
        remote_buffer=response_handler(remote_buffer)

        #如果有数据要传回本地客户端，发送它
        if len(remote_buffer):
            print("[==>] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer.encode())

    while True:
        local_buffer=receive_from(client_socket)#从本地client去接收数据

        if len(local_buffer):
            print("[==>] Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)
            #对请求进行处理
            local_buffer=request_handler(local_buffer)
            #发送至远程主机
            remote_socket.send(local_buffer.encode())
        #接收远程主机响应的数据
        remote_buffer=receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received %d bytes feom remote." % len(remote_buffer))
            #十六进制处理、
            hexdump(remote_buffer)
            #做响应处理
            remote_buffer=response_handler(remote_buffer)
            #将响应发送到本地终端
            client_socket.send(remote_buffer)

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data,Closing connections.")
            break



def main():
    parse=argparse.ArgumentParser(description='proxy')
    parse.add_argument("local_host",type=str)
    parse.add_argument("local_port",type=int)
    parse.add_argument("remote_host",type=str)
    parse.add_argument("remote_port",type=int)
    parse.add_argument("receive_first",type=str)
    args=parse.parse_args()#解析命令行参数

    receive_first=True if "True" in args.receive_first else False

    server_loop(args.local_host,args.local_port,args.remote_host,args.remote_port,args.receive_first)


if __name__ == '__main__':
    main()