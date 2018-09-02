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
from ctypes import *

# 监听的主机
host = "192.168.1.145"

# ip头定义
class IP(Structure):
    _fields_ =[
        ("ih1", c_ubyte, 4),
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
        # 协议字段与协议名称对应
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}
        # 可读性更强的IP地址
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

# 下面的代码类似于之前的例子

# 创建原始套接字， 然后绑定在公开接口上
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))

# 设置在捕获的数据包中包含ip头
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# 在windows平台上，我们需要设置IOCTL以启用混杂模式
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        # 读取数据包
        raw_buffer = sniffer.recvfrom(65565)[0]

        # 将缓冲区的前20个字节按IP头进行解析
        ip_header =IP(raw_buffer[0: 20])

        # 输出协议和通信双方IP地址
        print("protocol: %s %s -> %s"%(ip_header.protocol, ip_header.src_address, ip_header.dst_address))

# 处理Ctrl+C
except KeyboardInterrupt:
    # 如果运行在windows上， 关闭混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

