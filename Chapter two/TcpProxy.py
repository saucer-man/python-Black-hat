# -*- coding:utf-8 -*-
# version : python3.5
# description : https://xiaogeng.top/python/55.html

import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Fail to listen on %s: %d" % (local_host, local_port))
        print("[!!] Check for other listening sockets correct permissions.")
        sys.exit(0)
    print("[*] Listening on %s: %d" %(local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()

        # 打印出本地连接信息
        print("[>>==] Received incoming connection from %s: %d" %(addr[0], addr[1]))

        # 开启一个线程与远程主机通信
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    #连接远程主机
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # 如果必要从远程主机接收数据
    if receive_first:
        remote_buffer =  receive_from(remote_socket)
        hexdump(remote_buffer)

        # 发送给我们的响应处理
        remote_buffer = response_handler(remote_buffer)

        # 如果我们有数据传递给本地客户端，发送它
        if len(remote_buffer):
            print("[<<==] Sending %d bytes to localhost."%len(remote_buffer))
            client_socket.send(remote_buffer)

    # 现在我们从本地循环读取数据。发送给远程主机和本地主机
    while True:
        # 从本地读取数据
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("[>>==] Received %d bytes from localhost."%len(local_buffer))

            hexdump(local_buffer)
            # 发送给我们的本地请求
            local_buffer = request_handler(local_buffer)
            # 向远程主机发送数据
            remote_socket.send(local_buffer)
            print("[==>>] Sent to remote.")

        # 接收响应的数据
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[==<<] Received %d bytes from remote. " % len(remote_buffer))
            hexdump(remote_buffer)
            # 发送到响应处理函数
            remote_buffer = response_handler(remote_buffer)
            # 将响应发送给本地socket
            client_socket.send(remote_buffer)
            print("[<<==] Sent to localhost")

        # 如果两边都没有数据，关闭连接
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2

    for i in range(0, len(src), length):
        s = src[i:i + length]
        hexa = ' '.join([hex(x)[2:].upper().zfill(digits) for x in s])
        text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s])
        result.append("{0:04X}".format(i) + ' ' * 3 + hexa.ljust(length * (digits + 1)) + ' ' * 3 + "{0}".format(text))

    # return '\n'.join(result)
    print('\n'.join(result))

def receive_from(connection):
    buffer= ""

    # 我们设置了两秒的超时，这取决于目标的情况，肯需要调整
    connection.settimeout(2)

    try:
        # 持续从缓存中读取数据，直到没有数据或超时
        while True:
            data = connection.recv(4096)
            if not data:
                break
            data = bytes.decode(data)
            buffer += data
            buffer = str.encode(buffer)       
    except:
        pass
    return buffer

# 对目标是远程主机的请求进行修改
def request_handler(buffer):
    # 执行包修改
    return buffer

# 对目标是本地主机的响应进行修改
def response_handler(buffer):
    # 执行包修改
    return buffer

def main():
     if len(sys.argv[1:])!=5:
         print("Usage: ./proxy.py [localhost][localport][remotehost][remoteport][receive_first]")
         sys.exit(0)
     # 设置本地监听参数
     local_host = sys.argv[1]
     local_port = int(sys.argv[2])

     # 设置远程目标
     remote_host = sys.argv[3]
     remote_port = int(sys.argv[4])

     # 告诉代理在发送给远程主机之前连接和接收数据
     receive_first = sys.argv[5]

     if 'True' in receive_first:
         receive_first = True
     else:
         receive_first = False

     # 现在我们设置好我们的监听socket
     server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()
