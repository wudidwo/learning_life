import threading
import paramiko
import subprocess

def ssh_command(ip,user,passwd,command):
    client=paramiko.SSHClient()
    #client.load_host_keys('/home/wudidwo/.ssh/know_hosts') 密钥认证，可代替密码认证
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())#自动接受新的主机密钥并将其添加到本地的 known_hosts 文件中
    client.connect(ip,username=user,password=passwd)
    ssh_session=client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print(ssh_session.recv(1024))
    return

if __name__ == '__main__':
    ssh_command('172.20.10.3','wudidwo','lovegsh0510','id')