import sys
import socket
import getopt #分析处理参数
import threading
import subprocess #用于执行命令

#定义全局变量
listen           =False
command          =False
upload           =False
execute          =None
target           =None
upload_destination =None
port             =None


def usage():
    print("nat net tool")
    print()
    print("Usage:python3 natnet.py -t target_host -p port")
    print("-l --listen                  -listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run     -execute the given file upon receiving a connection")
    print("-c --command                 -initialize a command shell")
    print("-u --upload=destination      -upon receiving connection a file and write to [destination]")
    sys.exit(0)

def main():
    global listen
    global command
    global upload
    global execute
    global target
    global upload_destination
    global port

    #如果为输入参数
    if not len(sys.argv[1:]):
        usage()

    #读取命令行选项
    try:
        opts,argv=getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print(err)
        usage()



    for o,a in opts:                          #o是选项，a是参数
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen=True
        elif o in ("-c","--command"):
            command=True
        elif o in ("-e,--execute"):
            execute=a
        elif o in ("-t,--target"):
            target=a
        elif o in ("-p,--port"):
            port=int(a)
        elif o in ("-u","--upload"):
            upload_destination=a
        else:
            assert False,"Unhandle Option"#抛出异常Unhandle_Option



    #如果只是单纯发送数据，并不监听端口
    if not listen and target is not None and port > 0:
        print("DBG: read data from stdin")
        buffer = sys.stdin.read()

        client_sender(buffer) #发送数据

    if listen:
        server_loop()




def client_sender(buffer):
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        client.connect((target,port))

        if len(buffer):
            client.send(buffer.encode('utf-8'))

        while True:
            recv_len=1
            response=""

            while recv_len:
                data=client.recv(4096)
                recv_len=len(data)
                response+=data.decode(errors='ignore')
                if recv_len < 4096:
                    break

            print(response)

            #接着交互
            buffer=input("")
            buffer+="\n" #输入处理，使得能与shell兼容
            client.send(buffer.encode('utf-8'))

    except:
        print("[*] Exception Exiting")
    finally:
        client.close()



def server_loop():
    global target

    if not target:
        target="0.0.0.0"

    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket,addr=server.accept()

        client_tread=threading.Thread(target=client_handler,args=(client_socket,))

        client_tread.start()




def run_command(command):
    #换行
    command=command.rstrip()

    try:
        output=subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except:
        output="Failed to EXECUTE command.\r\n"

    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    #检测文件上传
    if upload_destination is not None:
        file_buffer=None

        while True:
            data=client_socket.recv(4096).decode('utf-8')
            if not data:
                break
            else:
                file_buffer+=data

        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send("successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Filed to save file to %s\r\n" % upload_destination)

    #检测命令执行
    if execute is not None:
        output=run_command(execute)

        client_socket.send(output.encode('utf-8'))


    if command:
        while True:
            client_socket.send("<NATCAT:#>".encode('utf-8'))

            #接收命令直到换行符
            cmd_buffer=""
            if "\n" not in cmd_buffer:
                data=client_socket.recv(1024).decode('utf-8')
                cmd_buffer+=data
                response=run_command(cmd_buffer)

                client_socket.send(response.encode())

if __name__ == '__main__':
    main()








