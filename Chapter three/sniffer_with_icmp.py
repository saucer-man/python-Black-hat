# encoding:utf-8
"""
源代码在kali2 64上运行会出现错误：`Buffer size too small (20 instead of at least 32 bytes)`
解决方法可参考：
https://stackoverflow.com/questions/29306747/python-sniffing-from-black-hat-python-book
修改
```
("src",           c_ulong),
("dst",           c_ulong)  
self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))
```
为
```
("src",           c_uint32),
("dst",           c_uint32)  
self.src_address = socket.inet_ntoa(struct.pack("@I",self.src))
self.dst_address = socket.inet_ntoa(struct.pack("@I",self.dst))
```
"""

import socket
import os
import struct
# import threading

from ctypes import *

# 监听的主机
host = "192.168.1.145"


class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_uint32),
        ("dst", c_uint32)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # 转换为可读性更强的ip地址
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # 可读性更强的协议
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
        ("type", c_ubyte),
        ("code", c_ubyte),
        ("checksum", c_ushort),
        ("unused", c_ushort),
        ("next_hop_mtu", c_ushort)
    ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


# 创建一个新的套接字，并绑定到公开接口上
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# 让捕获的数据中包含IP头
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# 在windows平台上，我们需要设置IOCTL以启用混杂模式
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:

        # 读取数据包
        raw_buffer = sniffer.recvfrom(65565)[0]

        # 将缓冲区的前20个字节按IP头进行解析
        ip_header = IP(raw_buffer[0:20])

        # 输出协议和通信双方IP地址
        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))


        # 如果是ICMP协议，进行处理
        if ip_header.protocol == "ICMP":
            # 计算ICMP包的起始位置
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # 解析ICMP数据
            icmp_header = ICMP(buf)

            print("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

# 处理Ctrl+C
except KeyboardInterrupt:
    # 如果运行在windows上， 关闭混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

