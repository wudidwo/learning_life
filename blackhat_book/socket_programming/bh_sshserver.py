import socket
import paramiko
import threading
import sys

host_key=paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface): #server继承paramkio.ServerImterface,这里的参数使用于处理服务端身份验证和通道请求的接口
    def __init__(self):
        self.event=threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if username=='wudidwo' and password=='lovegsh0510':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])

try:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)#socket.SO_REUSEADDR是允许端口复用，省去TIME_WAIT的时间
    sock.bind((server,ssh_port))
    sock.listen(100)
    print('[+] listen on connection ...')
    client,addr=sock.accept()
except Exception as e:
    print('[-] listen failed '+ str(e))
    sys.exit(1)
print('[+] Got a connection!')


try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print('[-] SSH negotiation failed.')
    chan = bhSession.accept(20) # 等待客户端连接，超时时间为20秒
    print('[+] Authenticated!')
    print(chan.recv(1024).decode())
    chan.send('welcome to bh_ssh')
    while True:
        try:
            coommand=input('Enter commend:').strip('\n')
            if coommand != 'exit':
                chan.send(coommand)
                print(chan.recv(1024).decode(errors='ignore') + '\n')
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print('[-] Caught exception:' + str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)












