import socket
import os
import struct
from ctypes import *

host='172.20.10.2'

class IP(Structure):#Structure是个类，IP继承这个类
    _fields_ = [
        ("ih1",             c_ubyte, 4),
        ("version",         c_ubyte, 4),
        ("tos",             c_ubyte),
        ("len",             c_ushort),
        ("id",              c_ushort),
        ("offset",          c_ushort),
        ("ttl",             c_ubyte),
        ("protocol_num",    c_ubyte),
        ("sum",             c_ushort),
        ("src",             c_ulong),
        ("dst",             c_ulong)
    ]

    #构造函数，用于创建对象
    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    #构造函数，用于初始化对象
    def __init__(self,socket_buffer=None):
        self.protocol_map = {1:"ICMP",6:"TCP",17:"UDP"}

        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        #协议类型
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
        ("type",c_ubyte),
        ("code",c_ubyte),
        ("checksum",c_ushort),
        ("unused",c_ushort),
        ("next_hop_mtu",c_ushort)
    ]

    def __new__(self,socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self):
        pass


if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket_protocol)

sniffer.bind((host,0))

sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1)

if os.name=="nt":
    sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_ON)

try:
    while True:

        #读取数据包
        raw_buffer = sniffer.recvfrom(65565)[0]

        #将缓冲区的前20字节按照ip头进行解析
        ip_header = IP(raw_buffer[0:20])

        print("Protocol: {0} {1} -> {2}".format(ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        if ip_header.protocol=="ICMP":
            offset = ip_header.ih1 * 4
            buff = raw_buffer[offset:offset + sizeof(ICMP)]

            icmp_header = ICMP(buff)

            print(print("ICMP -> Type: {0} Code: {1}".format(icmp_header.type, icmp_header.code)))

except KeyboardInterrupt:
    if os.name== "nt":
        sniffer.ioctl(socket.SIO_RCVALL,socket.RCVALL_OFF)