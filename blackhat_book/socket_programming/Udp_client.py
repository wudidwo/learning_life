import socket

udp_address=('www.baidu.com',80)

udp_client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
try:
    data="百度翻译"
    udp_client.sendto(data.encode('utf-8'),udp_address)
except Exception as e:
    print(e)
else:
    data,addr=udp_client.recvfrom(7895)#接收数据
    print(data)
finally:
    udp_client.close()