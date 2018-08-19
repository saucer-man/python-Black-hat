# -*- coding:utf-8 -*-
# version : python3.5
# description : https://xiaogeng.top/python/57.html

import socket
import paramiko
import threading
import sys

# 使用paramiko示例文件的密钥
host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if(username == 'justin') and (password == 'lovesthepython'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.setsockopt(sock, sock.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((server, ssh_port))
    sock.listen(100)
    print("[+] Listening for connection...")
    client, addr = sock.accept()
except Exception as e:
    print("[-] Listen failed: " + str(e))
    sys.exit(1)
print("[+] Got a connection ! ")

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print("[-] SSH negotiation failed.")
    chan = bhSession.accept(20)
    print("[+] Authenticated")
    print(chan.recv(1024).decode())
    chan.send(b'Welcome to bh_ssh')
    while True:
        try:
            command = input("Enter command: ").strip('\n')
            if command != 'exit':
                chan.send(command)
                print(chan.recv(1024).decode()+'\n')
            else:
                chan.send(b'exit')
                print("exiting")
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print("[-] Caught exception: "+str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)


